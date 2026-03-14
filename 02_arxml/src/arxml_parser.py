"""
AUTOSAR XML (ARXML) 文件解析模块

该模块负责解析ARXML文件，提取其中的元素信息，
包括AR-PACKAGES、ELEMENTS、SHORT-NAME等关键内容。
"""

from lxml import etree
from typing import Dict, List, Any, Optional
from pathlib import Path


class ARXMLParser:
    """ARXML文件解析器"""
    
    # AUTOSAR命名空间映射
    NAMESPACES = {
        'ar': 'http://autosar.org/schema/r4.0',
    }
    
    def __init__(self):
        """初始化解析器"""
        self.tree: Optional[etree._ElementTree] = None
        self.root: Optional[etree._Element] = None
        self.data: Dict[str, Any] = {}
        
    def load_file(self, file_path: str) -> bool:
        """
        加载ARXML文件
        
        Args:
            file_path: ARXML文件路径
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        try:
            # 解析XML文件
            self.tree = etree.parse(file_path)
            self.root = self.tree.getroot()
            
            # 检测命名空间
            self._detect_namespace()
            
            return True
        except Exception as e:
            print(f"加载文件失败: {e}")
            return False
    
    def _detect_namespace(self):
        """检测并更新命名空间"""
        if self.root is not None:
            # 获取根元素的命名空间
            ns = self.root.nsmap.get(None, '')
            if ns:
                self.NAMESPACES['ar'] = ns
    
    def parse(self) -> Dict[str, Any]:
        """
        解析ARXML文件内容
        
        Returns:
            Dict: 解析后的数据结构
        """
        if self.root is None:
            return {}
        
        self.data = {
            'file_info': self._get_file_info(),
            'packages': self._parse_packages(),
        }
        
        return self.data
    
    def _get_file_info(self) -> Dict[str, str]:
        """获取文件基本信息"""
        info = {
            'schema_version': '',
            'admin_data': {},
        }
        
        if self.root is not None:
            # 获取schema版本
            info['schema_version'] = self.root.attrib.get(
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', ''
            )
            
            # 获取ADMIN-DATA（如果存在）
            admin_data = self.root.find('.//ar:ADMIN-DATA', self.NAMESPACES)
            if admin_data is not None:
                info['admin_data'] = self._element_to_dict(admin_data)
        
        return info
    
    def _parse_packages(self) -> List[Dict[str, Any]]:
        """解析AR-PACKAGES（仅顶层包）"""
        packages = []
        
        if self.root is None:
            return packages
        
        # 只查找直接位于AR-PACKAGES下的AR-PACKAGE元素（顶层包）
        ar_packages_container = self.root.find('ar:AR-PACKAGES', self.NAMESPACES)
        if ar_packages_container is None:
            ar_packages_container = self.root.find('AR-PACKAGES')
        
        if ar_packages_container is not None:
            for pkg in ar_packages_container:
                # 跳过非元素节点（如注释）
                if not isinstance(pkg.tag, str):
                    continue
                local_tag = self._get_local_name(pkg.tag)
                if local_tag == 'AR-PACKAGE':
                    package_data = self._parse_package(pkg)
                    if package_data:
                        packages.append(package_data)
        
        return packages
    
    def _parse_package(self, package_element: etree._Element) -> Dict[str, Any]:
        """解析单个AR-PACKAGE"""
        pkg_data = {
            'short_name': self._get_short_name(package_element),
            'long_name': self._get_long_name(package_element),
            'description': self._get_description(package_element),
            'elements': [],
            'sub_packages': [],
        }
        
        # 解析ELEMENTS
        elements = package_element.find('ar:ELEMENTS', self.NAMESPACES)
        if elements is None:
            elements = package_element.find('ELEMENTS')
        
        if elements is not None:
            for elem in elements:
                # 跳过非元素节点（如注释）
                if not isinstance(elem.tag, str):
                    continue
                elem_data = self._parse_element(elem)
                if elem_data:
                    pkg_data['elements'].append(elem_data)
        
        # 解析子包
        sub_packages = package_element.find('ar:AR-PACKAGES', self.NAMESPACES)
        if sub_packages is None:
            sub_packages = package_element.find('AR-PACKAGES')
        
        if sub_packages is not None:
            for sub_pkg in sub_packages:
                # 跳过非元素节点（如注释）
                if not isinstance(sub_pkg.tag, str):
                    continue
                local_tag = self._get_local_name(sub_pkg.tag)
                if local_tag == 'AR-PACKAGE':
                    sub_pkg_data = self._parse_package(sub_pkg)
                    if sub_pkg_data:
                        pkg_data['sub_packages'].append(sub_pkg_data)
        
        return pkg_data
    
    def _parse_element(self, element: etree._Element) -> Dict[str, Any]:
        """解析ELEMENTS中的元素"""
        # 获取元素类型（标签名）
        tag = self._get_local_name(element.tag)
        
        elem_data = {
            'type': tag,
            'short_name': self._get_short_name(element),
            'long_name': self._get_long_name(element),
            'description': self._get_description(element),
            'category': self._get_text_content(element, 'CATEGORY'),
            'attributes': {},
            'children': [],
        }
        
        # 根据元素类型解析特定属性
        if tag == 'APPLICATION-SW-COMPONENT-TYPE':
            elem_data['attributes'] = self._parse_swc_type(element)
        elif tag == 'SENDER-RECEIVER-INTERFACE':
            elem_data['attributes'] = self._parse_sr_interface(element)
        elif tag == 'CLIENT-SERVER-INTERFACE':
            elem_data['attributes'] = self._parse_cs_interface(element)
        elif tag == 'IMPLEMENTATION-DATA-TYPE':
            elem_data['attributes'] = self._parse_impl_data_type(element)
        elif tag == 'APPLICATION-PRIMITIVE-DATA-TYPE':
            elem_data['attributes'] = self._parse_app_data_type(element)
        elif tag == 'COMPU-METHOD':
            elem_data['attributes'] = self._parse_compu_method(element)
        elif tag == 'UNIT':
            elem_data['attributes'] = self._parse_unit(element)
        elif tag == 'SW-BASE-TYPE':
            elem_data['attributes'] = self._parse_base_type(element)
        else:
            # 通用属性解析
            elem_data['attributes'] = self._parse_generic_attributes(element)
        
        return elem_data
    
    def _parse_swc_type(self, element: etree._Element) -> Dict[str, Any]:
        """解析软件组件类型"""
        attrs = {
            'ports': [],
            'internal_behaviors': [],
        }
        
        # 解析端口
        ports = element.find('ar:PORTS', self.NAMESPACES)
        if ports is None:
            ports = element.find('PORTS')
        
        if ports is not None:
            for port in ports:
                port_data = {
                    'name': self._get_short_name(port),
                    'type': self._get_local_name(port.tag),
                    'interface_ref': self._get_ref(port, 'PROVIDED-INTERFACE-TREF') or 
                                     self._get_ref(port, 'REQUIRED-INTERFACE-TREF'),
                }
                attrs['ports'].append(port_data)
        
        return attrs
    
    def _parse_sr_interface(self, element: etree._Element) -> Dict[str, Any]:
        """解析发送接收接口"""
        attrs = {
            'data_elements': [],
        }
        
        # 解析数据元素
        data_elements = element.find('ar:DATA-ELEMENTS', self.NAMESPACES)
        if data_elements is None:
            data_elements = element.find('DATA-ELEMENTS')
        
        if data_elements is not None:
            for de in data_elements:
                de_data = {
                    'name': self._get_short_name(de),
                    'type_ref': self._get_ref(de, 'TYPE-TREF'),
                }
                attrs['data_elements'].append(de_data)
        
        return attrs
    
    def _parse_cs_interface(self, element: etree._Element) -> Dict[str, Any]:
        """解析客户端服务端接口"""
        attrs = {
            'operations': [],
        }
        
        # 解析操作
        operations = element.find('ar:OPERATIONS', self.NAMESPACES)
        if operations is None:
            operations = element.find('OPERATIONS')
        
        if operations is not None:
            for op in operations:
                op_data = {
                    'name': self._get_short_name(op),
                    'arguments': [],
                }
                
                # 解析参数
                arguments = op.find('ar:ARGUMENTS', self.NAMESPACES)
                if arguments is None:
                    arguments = op.find('ARGUMENTS')
                
                if arguments is not None:
                    for arg in arguments:
                        arg_data = {
                            'name': self._get_short_name(arg),
                            'direction': self._get_text_content(arg, 'DIRECTION'),
                            'type_ref': self._get_ref(arg, 'TYPE-TREF'),
                        }
                        op_data['arguments'].append(arg_data)
                
                attrs['operations'].append(op_data)
        
        return attrs
    
    def _parse_impl_data_type(self, element: etree._Element) -> Dict[str, Any]:
        """解析实现数据类型"""
        attrs = {
            'category': self._get_text_content(element, 'CATEGORY'),
            'base_type_ref': '',
            'compu_method_ref': '',
        }
        
        # 查找SW-DATA-DEF-PROPS
        sw_props = element.find('.//ar:SW-DATA-DEF-PROPS-VARIANTS', self.NAMESPACES)
        if sw_props is None:
            sw_props = element.find('.//SW-DATA-DEF-PROPS-VARIANTS')
        
        if sw_props is not None:
            attrs['base_type_ref'] = self._get_ref(sw_props, 'BASE-TYPE-REF')
            attrs['compu_method_ref'] = self._get_ref(sw_props, 'COMPU-METHOD-REF')
        
        return attrs
    
    def _parse_app_data_type(self, element: etree._Element) -> Dict[str, Any]:
        """解析应用数据类型"""
        attrs = {
            'category': self._get_text_content(element, 'CATEGORY'),
            'unit_ref': '',
            'compu_method_ref': '',
        }
        
        sw_props = element.find('.//ar:SW-DATA-DEF-PROPS-VARIANTS', self.NAMESPACES)
        if sw_props is None:
            sw_props = element.find('.//SW-DATA-DEF-PROPS-VARIANTS')
        
        if sw_props is not None:
            attrs['unit_ref'] = self._get_ref(sw_props, 'UNIT-REF')
            attrs['compu_method_ref'] = self._get_ref(sw_props, 'COMPU-METHOD-REF')
        
        return attrs
    
    def _parse_compu_method(self, element: etree._Element) -> Dict[str, Any]:
        """解析计算方法"""
        attrs = {
            'category': self._get_text_content(element, 'CATEGORY'),
            'unit_ref': self._get_ref(element, 'UNIT-REF'),
        }
        return attrs
    
    def _parse_unit(self, element: etree._Element) -> Dict[str, Any]:
        """解析单位"""
        attrs = {
            'display_name': self._get_text_content(element, 'DISPLAY-NAME'),
            'factor': self._get_text_content(element, 'FACTOR-SI-TO-UNIT'),
            'offset': self._get_text_content(element, 'OFFSET-SI-TO-UNIT'),
        }
        return attrs
    
    def _parse_base_type(self, element: etree._Element) -> Dict[str, Any]:
        """解析基础类型"""
        attrs = {
            'category': self._get_text_content(element, 'CATEGORY'),
            'size': self._get_text_content(element, 'BASE-TYPE-SIZE'),
            'encoding': self._get_text_content(element, 'BASE-TYPE-ENCODING'),
            'native_declaration': self._get_text_content(element, 'NATIVE-DECLARATION'),
        }
        return attrs
    
    def _parse_generic_attributes(self, element: etree._Element) -> Dict[str, Any]:
        """通用属性解析"""
        attrs = {}
        
        for child in element:
            tag = self._get_local_name(child.tag)
            if tag not in ['SHORT-NAME', 'LONG-NAME', 'DESC', 'ADMIN-DATA']:
                if len(child) == 0:
                    # 叶子节点
                    if child.text:
                        attrs[tag] = child.text.strip()
                else:
                    # 有子节点，递归解析
                    attrs[tag] = self._element_to_dict(child)
        
        return attrs
    
    def _element_to_dict(self, element: etree._Element) -> Dict[str, Any]:
        """将XML元素转换为字典"""
        result = {}
        
        for child in element:
            tag = self._get_local_name(child.tag)
            if len(child) == 0:
                result[tag] = child.text.strip() if child.text else ''
            else:
                result[tag] = self._element_to_dict(child)
        
        return result
    
    def _get_short_name(self, element: etree._Element) -> str:
        """获取SHORT-NAME"""
        short_name = element.find('ar:SHORT-NAME', self.NAMESPACES)
        if short_name is None:
            short_name = element.find('SHORT-NAME')
        return short_name.text.strip() if short_name is not None and short_name.text else ''
    
    def _get_long_name(self, element: etree._Element) -> str:
        """获取LONG-NAME"""
        long_name = element.find('.//ar:LONG-NAME/ar:L-4', self.NAMESPACES)
        if long_name is None:
            long_name = element.find('.//LONG-NAME/L-4')
        return long_name.text.strip() if long_name is not None and long_name.text else ''
    
    def _get_description(self, element: etree._Element) -> str:
        """获取描述信息"""
        desc = element.find('.//ar:DESC/ar:L-2', self.NAMESPACES)
        if desc is None:
            desc = element.find('.//DESC/L-2')
        return desc.text.strip() if desc is not None and desc.text else ''
    
    def _get_text_content(self, element: etree._Element, tag: str) -> str:
        """获取指定标签的文本内容"""
        child = element.find(f'ar:{tag}', self.NAMESPACES)
        if child is None:
            child = element.find(tag)
        return child.text.strip() if child is not None and child.text else ''
    
    def _get_ref(self, element: etree._Element, ref_tag: str) -> str:
        """获取引用路径"""
        ref = element.find(f'.//ar:{ref_tag}', self.NAMESPACES)
        if ref is None:
            ref = element.find(f'.//{ref_tag}')
        return ref.text.strip() if ref is not None and ref.text else ''
    
    @staticmethod
    def _get_local_name(tag) -> str:
        """获取不带命名空间的标签名"""
        # 处理非字符串类型（如lxml的函数对象，表示注释等特殊节点）
        if not isinstance(tag, str):
            return ''
        if '}' in tag:
            return tag.split('}')[1]
        return tag
    
    def get_flat_data(self) -> List[Dict[str, Any]]:
        """
        获取扁平化的数据，用于Excel导出
        
        Returns:
            List[Dict]: 扁平化的元素列表
        """
        flat_data = []
        
        if not self.data:
            return flat_data
        
        def process_package(pkg: Dict[str, Any], path: str = ''):
            current_path = f"{path}/{pkg['short_name']}" if path else pkg['short_name']
            
            # 处理元素
            for elem in pkg.get('elements', []):
                flat_elem = {
                    'package_path': current_path,
                    'element_type': elem.get('type', ''),
                    'short_name': elem.get('short_name', ''),
                    'long_name': elem.get('long_name', ''),
                    'description': elem.get('description', ''),
                    'category': elem.get('category', ''),
                }
                
                # 添加属性
                attrs = elem.get('attributes', {})
                for key, value in attrs.items():
                    if isinstance(value, (str, int, float)):
                        flat_elem[f'attr_{key}'] = value
                    elif isinstance(value, list):
                        flat_elem[f'attr_{key}'] = str(len(value)) + ' items'
                
                flat_data.append(flat_elem)
            
            # 递归处理子包
            for sub_pkg in pkg.get('sub_packages', []):
                process_package(sub_pkg, current_path)
        
        for pkg in self.data.get('packages', []):
            process_package(pkg)
        
        return flat_data


def parse_arxml_file(file_path: str) -> Dict[str, Any]:
    """
    解析ARXML文件的便捷函数
    
    Args:
        file_path: ARXML文件路径
        
    Returns:
        Dict: 解析后的数据
    """
    parser = ARXMLParser()
    if parser.load_file(file_path):
        return parser.parse()
    return {}
