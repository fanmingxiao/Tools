"""
DBC导出模块

该模块负责将解析后的ARXML数据导出为CANoe DBC文件格式。
DBC是Vector公司开发的CAN数据库文件格式，是汽车行业的事实标准。
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class DBCExporter:
    """DBC文件导出器"""
    
    def __init__(self):
        """初始化导出器"""
        self.messages: List[Dict[str, Any]] = []
        self.signals: Dict[int, List[Dict[str, Any]]] = {}  # message_id -> signals
        self.nodes: List[str] = []
        self.comments: List[Dict[str, Any]] = []
        self.value_tables: Dict[str, Dict[int, str]] = {}
        
        # 消息ID计数器（用于自动分配ID）
        self._message_id_counter = 0x100
        
    def export(self, data: Dict[str, Any], output_path: str) -> bool:
        """
        导出数据到DBC文件
        
        Args:
            data: 解析后的ARXML数据
            output_path: 输出文件路径
            
        Returns:
            bool: 导出成功返回True
        """
        try:
            # 清空之前的数据
            self._reset()
            
            # 从ARXML数据中提取信息
            self._extract_from_arxml(data)
            
            # 生成DBC内容
            dbc_content = self._generate_dbc_content()
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(dbc_content)
            
            return True
            
        except Exception as e:
            print(f"导出DBC失败: {e}")
            return False
    
    def _reset(self):
        """重置内部数据"""
        self.messages.clear()
        self.signals.clear()
        self.nodes.clear()
        self.comments.clear()
        self.value_tables.clear()
        self._message_id_counter = 0x100
    
    def _extract_from_arxml(self, data: Dict[str, Any]):
        """从ARXML数据中提取CAN相关信息"""
        
        def process_package(pkg: Dict[str, Any], path: str = ''):
            current_path = f"{path}/{pkg['short_name']}" if path else pkg['short_name']
            
            for elem in pkg.get('elements', []):
                elem_type = elem.get('type', '')
                
                # 软件组件 -> 节点
                if elem_type == 'APPLICATION-SW-COMPONENT-TYPE':
                    self._extract_node(elem)
                
                # 发送接收接口 -> 消息和信号
                elif elem_type == 'SENDER-RECEIVER-INTERFACE':
                    self._extract_sr_interface(elem, current_path)
                
                # 客户端服务端接口 -> 消息和信号
                elif elem_type == 'CLIENT-SERVER-INTERFACE':
                    self._extract_cs_interface(elem, current_path)
                
                # 实现数据类型 -> 用于信号属性
                elif elem_type == 'IMPLEMENTATION-DATA-TYPE':
                    self._extract_data_type(elem)
            
            # 递归处理子包
            for sub_pkg in pkg.get('sub_packages', []):
                process_package(sub_pkg, current_path)
        
        for pkg in data.get('packages', []):
            process_package(pkg)
    
    def _extract_node(self, elem: Dict[str, Any]):
        """提取节点信息"""
        short_name = elem.get('short_name', '')
        if short_name and short_name not in self.nodes:
            self.nodes.append(short_name)
            
            # 添加节点注释
            description = elem.get('description', '') or elem.get('long_name', '')
            if description:
                self.comments.append({
                    'type': 'BU_',
                    'name': short_name,
                    'comment': description
                })
    
    def _extract_sr_interface(self, elem: Dict[str, Any], path: str):
        """提取发送接收接口作为消息"""
        short_name = elem.get('short_name', '')
        if not short_name:
            return
        
        # 创建消息
        message_id = self._get_next_message_id()
        attrs = elem.get('attributes', {})
        data_elements = attrs.get('data_elements', [])
        
        # 计算DLC（数据长度）
        dlc = max(8, len(data_elements))  # 默认8字节
        
        message = {
            'id': message_id,
            'name': self._sanitize_name(short_name),
            'dlc': dlc,
            'transmitter': self.nodes[0] if self.nodes else 'Vector__XXX'
        }
        self.messages.append(message)
        
        # 添加消息注释
        description = elem.get('description', '') or elem.get('long_name', '')
        if description:
            self.comments.append({
                'type': 'BO_',
                'id': message_id,
                'comment': description
            })
        
        # 提取信号
        self.signals[message_id] = []
        start_bit = 0
        
        for de in data_elements:
            signal_name = de.get('name', 'Signal')
            signal = {
                'name': self._sanitize_name(signal_name),
                'start_bit': start_bit,
                'size': 8,  # 默认8位
                'byte_order': 1,  # 1=Little Endian (Intel)
                'value_type': '+',  # +表示无符号
                'factor': 1.0,
                'offset': 0.0,
                'min': 0.0,
                'max': 255.0,
                'unit': '',
                'receivers': ['Vector__XXX']
            }
            self.signals[message_id].append(signal)
            start_bit += 8
    
    def _extract_cs_interface(self, elem: Dict[str, Any], path: str):
        """提取客户端服务端接口作为消息"""
        short_name = elem.get('short_name', '')
        if not short_name:
            return
        
        attrs = elem.get('attributes', {})
        operations = attrs.get('operations', [])
        
        for op in operations:
            op_name = op.get('name', '')
            if not op_name:
                continue
            
            # 每个操作创建一个消息
            message_id = self._get_next_message_id()
            message_name = f"{self._sanitize_name(short_name)}_{self._sanitize_name(op_name)}"
            
            arguments = op.get('arguments', [])
            dlc = max(8, len(arguments) * 2)
            
            message = {
                'id': message_id,
                'name': message_name,
                'dlc': dlc,
                'transmitter': self.nodes[0] if self.nodes else 'Vector__XXX'
            }
            self.messages.append(message)
            
            # 提取参数作为信号
            self.signals[message_id] = []
            start_bit = 0
            
            for arg in arguments:
                arg_name = arg.get('name', 'Arg')
                direction = arg.get('direction', 'IN')
                
                signal = {
                    'name': self._sanitize_name(arg_name),
                    'start_bit': start_bit,
                    'size': 16,  # 默认16位
                    'byte_order': 1,
                    'value_type': '+' if direction == 'IN' else '-',
                    'factor': 1.0,
                    'offset': 0.0,
                    'min': 0.0,
                    'max': 65535.0,
                    'unit': '',
                    'receivers': ['Vector__XXX']
                }
                self.signals[message_id].append(signal)
                start_bit += 16
    
    def _extract_data_type(self, elem: Dict[str, Any]):
        """提取数据类型信息（用于后续信号属性）"""
        # 这里可以扩展以获取更详细的数据类型信息
        pass
    
    def _get_next_message_id(self) -> int:
        """获取下一个消息ID"""
        msg_id = self._message_id_counter
        self._message_id_counter += 1
        return msg_id
    
    def _sanitize_name(self, name: str) -> str:
        """清理名称，确保符合DBC命名规范"""
        # DBC名称只允许字母、数字和下划线
        result = ''
        for char in name:
            if char.isalnum() or char == '_':
                result += char
            else:
                result += '_'
        
        # 确保名称不以数字开头
        if result and result[0].isdigit():
            result = '_' + result
        
        return result or 'Unknown'
    
    def _generate_dbc_content(self) -> str:
        """生成DBC文件内容"""
        lines = []
        
        # 版本信息
        lines.append('VERSION ""')
        lines.append('')
        
        # 命名空间（通常为空）
        lines.append('NS_ :')
        lines.append('')
        
        # 总线速度设置
        lines.append('BS_:')
        lines.append('')
        
        # 节点列表
        if self.nodes:
            nodes_str = ' '.join(self.nodes)
            lines.append(f'BU_: {nodes_str}')
        else:
            lines.append('BU_:')
        lines.append('')
        
        # 消息定义
        for msg in self.messages:
            # BO_ message_id message_name: dlc transmitter
            lines.append(f"BO_ {msg['id']} {msg['name']}: {msg['dlc']} {msg['transmitter']}")
            
            # 信号定义
            for sig in self.signals.get(msg['id'], []):
                # SG_ signal_name : start_bit|size@byte_order value_type (factor,offset) [min|max] "unit" receivers
                receivers_str = ','.join(sig['receivers'])
                lines.append(
                    f" SG_ {sig['name']} : {sig['start_bit']}|{sig['size']}@{sig['byte_order']}{sig['value_type']} "
                    f"({sig['factor']},{sig['offset']}) [{sig['min']}|{sig['max']}] \"{sig['unit']}\" {receivers_str}"
                )
            
            lines.append('')
        
        # 注释
        for comment in self.comments:
            comment_text = comment['comment'].replace('"', "'").replace('\n', ' ')
            if comment['type'] == 'BU_':
                lines.append(f'CM_ BU_ {comment["name"]} "{comment_text}";')
            elif comment['type'] == 'BO_':
                lines.append(f'CM_ BO_ {comment["id"]} "{comment_text}";')
            elif comment['type'] == 'SG_':
                lines.append(f'CM_ SG_ {comment["id"]} {comment["name"]} "{comment_text}";')
        
        if self.comments:
            lines.append('')
        
        # 属性定义（可选）
        lines.append('BA_DEF_ BO_ "GenMsgCycleTime" INT 0 10000;')
        lines.append('BA_DEF_ SG_ "GenSigStartValue" INT 0 65535;')
        lines.append('')
        
        # 默认属性值
        lines.append('BA_DEF_DEF_ "GenMsgCycleTime" 100;')
        lines.append('BA_DEF_DEF_ "GenSigStartValue" 0;')
        lines.append('')
        
        return '\n'.join(lines)


def export_to_dbc(data: Dict[str, Any], output_path: str) -> bool:
    """
    导出到DBC的便捷函数
    
    Args:
        data: 解析后的ARXML数据
        output_path: 输出文件路径
        
    Returns:
        bool: 导出成功返回True
    """
    exporter = DBCExporter()
    return exporter.export(data, output_path)
