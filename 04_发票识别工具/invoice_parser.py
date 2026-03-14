# -*- coding: utf-8 -*-
"""
发票信息解析模块
从OCR识别结果中提取发票关键信息
"""

import re
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class InvoiceInfo:
    """发票信息数据类"""
    file_name: str = ""           # 文件名
    invoice_code: str = ""        # 发票代码
    invoice_number: str = ""      # 发票号码
    amount: float = 0.0           # 金额（不含税）
    tax_rate: str = ""            # 税率
    tax_amount: float = 0.0       # 税额
    total_amount: float = 0.0     # 价税合计
    invoice_date: str = ""        # 开票日期
    seller_name: str = ""         # 销售方名称
    buyer_name: str = ""          # 购买方名称
    remarks: str = ""             # 备注
    raw_text: str = ""            # 原始OCR文本
    # 出租车发票专用字段
    invoice_type: str = ""        # 发票类型（普通发票/出租车发票）
    taxi_number: str = ""         # 车牌号/车号
    pickup_time: str = ""         # 上车时间
    dropoff_time: str = ""        # 下车时间
    mileage: str = ""             # 里程
    wait_time: str = ""           # 等候时间


class InvoiceParser:
    """发票解析器类"""
    
    def __init__(self):
        """初始化解析器，编译正则表达式"""
        # ========== 发票代码模式（多种变体）==========
        self.invoice_code_patterns = [
            re.compile(r'发票代码[：:\s]*(\d{10,12})'),
            re.compile(r'发\s*票\s*代\s*码[：:\s]*(\d{10,12})'),
            re.compile(r'代码[：:\s]*(\d{10,12})'),
            re.compile(r'(\d{10,12})\s*发票代码'),
        ]
        
        # ========== 发票号码模式（多种变体）==========
        self.invoice_number_patterns = [
            re.compile(r'发票号码[：:\s]*(\d{8,20})'),
            re.compile(r'发\s*票\s*号\s*码[：:\s]*(\d{8,20})'),
            re.compile(r'号码[：:\s]*(\d{8,20})'),
            re.compile(r'No[\.:：]?\s*(\d{8,20})', re.IGNORECASE),
            re.compile(r'(\d{8,20})\s*发票号码'),
        ]
        
        # ========== 金额模式（价税合计/小写金额）==========
        self.total_amount_patterns = [
            # 价税合计（小写）模式
            re.compile(r'价税合计[（\(]?小写[）\)]?[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'[（\(]小写[）\)][：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'小写[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            # 价税合计模式
            re.compile(r'价税合计[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'价\s*税\s*合\s*计[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            # 合计/总计模式
            re.compile(r'合\s*计[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'总\s*计[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            # ¥符号后的金额（最后的金额通常是总额）
            re.compile(r'[¥￥]\s*([\d,，]+\.\d{2})'),
        ]
        
        # ========== 税额模式 ==========
        self.tax_amount_patterns = [
            re.compile(r'税\s*额[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'税\s*率[/／]税\s*额.*?[¥￥]?\s*([\d,，]+\.\d{2})'),
            re.compile(r'合计.*?税额[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'税额合计[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
        ]
        
        # ========== 不含税金额模式 ==========
        self.amount_patterns = [
            re.compile(r'金\s*额[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'合计.*?金额[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
            re.compile(r'(?<!价税)合\s*计[：:\s]*[¥￥]?\s*([\d,，]+\.?\d*)'),
        ]
        
        # ========== 税率模式 ==========
        self.tax_rate_patterns = [
            re.compile(r'税\s*率[：:\s]*(\d+\.?\d*)\s*%'),
            re.compile(r'(\d+\.?\d*)\s*%\s*(?:税率)?'),
            re.compile(r'税率[/／]税额.*?(\d+)%'),
        ]
        
        # ========== 日期模式 ==========
        self.date_patterns = [
            re.compile(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'),
            re.compile(r'开票日期[：:\s]*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})'),
            re.compile(r'日期[：:\s]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})'),
            re.compile(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'),
        ]
        
        # ========== 销售方名称模式 ==========
        self.seller_patterns = [
            re.compile(r'销售方.*?名\s*称[：:\s]*(.+?)(?:\n|纳税人|统一|地址|电话|$)'),
            re.compile(r'名\s*称[：:\s]*(.+?)(?:纳税人识别号|统一社会信用代码|地址|电话|$)'),
            re.compile(r'销[售方]*[：:\s]*(.+?公司)'),
        ]
        
        # ========== 出租车发票专用模式 ==========
        self.taxi_keywords = ['出租车', '出租汽车', 'TAXI', 'taxi', '打车', '客运出租']
        self.taxi_number_pattern = re.compile(r'车[号牌][：:\s]*([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-Z0-9]{4,6})')
        self.alt_taxi_number_pattern = re.compile(r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-Z0-9]{4,6})')
        self.pickup_time_pattern = re.compile(r'上车[时间]*[：:\s]*(\d{1,2}[：:]\d{2}(?:[：:]\d{2})?)')
        self.dropoff_time_pattern = re.compile(r'下车[时间]*[：:\s]*(\d{1,2}[：:]\d{2}(?:[：:]\d{2})?)')
        self.mileage_pattern = re.compile(r'里程[：:\s]*([\d.]+)\s*(?:公里|km|KM)?')
        self.wait_time_pattern = re.compile(r'等[候时间]*[：:\s]*([\d.]+)\s*(?:分钟|分|min)?')
    
    def _is_taxi_invoice(self, text: str) -> bool:
        """检测是否为出租车发票"""
        return any(keyword in text for keyword in self.taxi_keywords)
    
    def parse(self, ocr_items: List[dict], file_name: str = "") -> InvoiceInfo:
        """
        解析OCR识别结果，提取发票信息
        
        Args:
            ocr_items: OCR识别结果列表
            file_name: 发票文件名
            
        Returns:
            InvoiceInfo对象
        """
        # 合并所有文本
        all_text = '\n'.join([item['text'] for item in ocr_items])
        
        info = InvoiceInfo()
        info.file_name = file_name
        info.raw_text = all_text
        
        # 检测发票类型
        if self._is_taxi_invoice(all_text):
            info.invoice_type = "出租车发票"
            self._parse_taxi_invoice(info, all_text)
        else:
            info.invoice_type = "普通发票"
            self._parse_normal_invoice(info, all_text, ocr_items)
        
        return info
    
    def _parse_normal_invoice(self, info: InvoiceInfo, all_text: str, ocr_items: List[dict]):
        """解析普通发票"""
        # 提取发票代码（尝试多种模式）
        for pattern in self.invoice_code_patterns:
            match = pattern.search(all_text)
            if match:
                info.invoice_code = match.group(1)
                break
        
        # 提取发票号码（尝试多种模式）
        for pattern in self.invoice_number_patterns:
            match = pattern.search(all_text)
            if match:
                info.invoice_number = match.group(1)
                break
        
        # 提取价税合计（尝试多种模式）
        for pattern in self.total_amount_patterns:
            match = pattern.search(all_text)
            if match:
                amount = self._parse_number(match.group(1))
                if amount > 0:
                    info.total_amount = amount
                    break
        
        # 检测是否为免税发票
        # 免税发票的特征: 包含"免税"、"***"（税率位置）、"不征税"等关键词
        is_tax_free = False
        tax_free_patterns = ['免税', '***', '不征税', '0税率', '0%']
        for pattern in tax_free_patterns:
            if pattern in all_text:
                is_tax_free = True
                break
        
        if is_tax_free:
            # 免税发票：税额为0，税率为"免税"
            info.tax_amount = 0
            info.tax_rate = "免税"
            info.amount = info.total_amount
            print(f"[解析] 检测到免税发票")
        else:
            # 提取税额（尝试多种模式）
            for pattern in self.tax_amount_patterns:
                match = pattern.search(all_text)
                if match:
                    tax = self._parse_number(match.group(1))
                    if tax > 0 and (info.total_amount == 0 or tax < info.total_amount):
                        info.tax_amount = tax
                        break
            
            # 如果没有提取到税额，尝试从"金额"和"税额"的多次出现中提取
            if info.tax_amount == 0 and info.total_amount > 0:
                # 尝试查找所有¥金额，通常格式是：金额¥xxx  税额¥xxx  价税合计¥xxx
                money_pattern = re.compile(r'[¥￥]\s*([\d,，]+\.?\d*)')
                amounts = []
                for m in money_pattern.finditer(all_text):
                    val = self._parse_number(m.group(1))
                    if val > 0:
                        amounts.append(val)
                
                # 如果有3个以上金额，最后一个通常是价税合计，倒数第二个之前的可能是税额
                if len(amounts) >= 2:
                    # 尝试找到税额（应该小于总额）
                    for amt in amounts:
                        if 0 < amt < info.total_amount and amt != info.total_amount:
                            # 检查是否可能是税额（一般税额较小）
                            if amt < info.total_amount * 0.3:  # 税率一般不超过30%
                                info.tax_amount = amt
                                break
            
            # 计算不含税金额
            if info.total_amount > 0 and info.tax_amount > 0:
                info.amount = round(info.total_amount - info.tax_amount, 2)
            elif info.total_amount > 0:
                info.amount = info.total_amount
        
        # 提取税率
        for pattern in self.tax_rate_patterns:
            match = pattern.search(all_text)
            if match:
                rate = match.group(1)
                # 验证税率在合理范围内（0-30%）
                try:
                    rate_val = float(rate)
                    if 0 < rate_val <= 30:
                        info.tax_rate = f"{rate}%"
                        break
                except ValueError:
                    continue
        
        # 如果没有找到税率但有税额和总额，计算税率
        if not info.tax_rate and info.tax_amount > 0 and info.amount > 0:
            calculated_rate = round(info.tax_amount / info.amount * 100, 1)
            if 0 < calculated_rate <= 30:
                info.tax_rate = f"{calculated_rate}%"
        
        # 提取日期
        info.invoice_date = self._extract_date(all_text)
        
        # 提取销售方名称
        info.seller_name = self._extract_seller(all_text, ocr_items)
    
    def _parse_taxi_invoice(self, info: InvoiceInfo, all_text: str):
        """解析出租车发票"""
        # 提取发票代码
        match = self.invoice_code_pattern.search(all_text)
        if match:
            info.invoice_code = match.group(1)
        
        # 提取发票号码
        match = self.invoice_number_pattern.search(all_text)
        if match:
            info.invoice_number = match.group(1)
        else:
            match = self.alt_number_pattern.search(all_text)
            if match:
                info.invoice_number = match.group(1)
        
        # 提取车牌号
        match = self.taxi_number_pattern.search(all_text)
        if match:
            info.taxi_number = match.group(1)
        else:
            match = self.alt_taxi_number_pattern.search(all_text)
            if match:
                info.taxi_number = match.group(1)
        
        # 提取上车时间
        match = self.pickup_time_pattern.search(all_text)
        if match:
            info.pickup_time = match.group(1).replace('：', ':')
        
        # 提取下车时间
        match = self.dropoff_time_pattern.search(all_text)
        if match:
            info.dropoff_time = match.group(1).replace('：', ':')
        
        # 提取里程
        match = self.mileage_pattern.search(all_text)
        if match:
            info.mileage = match.group(1) + " 公里"
        else:
            match = self.alt_mileage_pattern.search(all_text)
            if match:
                info.mileage = match.group(1) + " 公里"
        
        # 提取等候时间
        match = self.wait_time_pattern.search(all_text)
        if match:
            info.wait_time = match.group(1) + " 分钟"
        
        # 提取金额
        match = self.taxi_amount_pattern.search(all_text)
        if match:
            info.total_amount = self._parse_number(match.group(1))
        else:
            # 尝试找最后一个金额（通常是总金额）
            matches = list(self.taxi_total_pattern.finditer(all_text))
            if matches:
                info.total_amount = self._parse_number(matches[-1].group(1))
        
        info.amount = info.total_amount  # 出租车发票通常不含税
        
        # 提取日期
        info.invoice_date = self._extract_date(all_text)
        
        # 销售方通常是出租车公司
        if '公司' in all_text:
            # 尝试提取公司名称
            company_pattern = re.compile(r'([^\n]{2,20}(?:出租|客运|交通)[^\n]{0,10}公司)')
            match = company_pattern.search(all_text)
            if match:
                info.seller_name = match.group(1)
    
    def _extract_amount(self, text: str) -> float:
        """提取金额"""
        # 尝试多种模式
        patterns = [
            self.alt_amount_pattern,
            self.amount_pattern,
            self.total_pattern
        ]
        
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return self._parse_number(match.group(1))
        
        return 0.0
    
    def _parse_number(self, num_str: str) -> float:
        """解析数字字符串为浮点数"""
        try:
            # 移除逗号和空格
            clean = num_str.replace(',', '').replace(' ', '').replace('，', '')
            return float(clean)
        except ValueError:
            return 0.0
    
    def _extract_date(self, text: str) -> str:
        """提取日期"""
        for pattern in self.date_patterns:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    # 完整日期字符串
                    return groups[0].replace('/', '-')
                elif len(groups) == 3:
                    # 年月日分开
                    year, month, day = groups
                    return f"{year}-{int(month):02d}-{int(day):02d}"
        return ""
    
    def _extract_seller(self, text: str, ocr_items: List[dict]) -> str:
        """提取销售方名称"""
        # 查找"销售方"关键词后的公司名称
        lines = text.split('\n')
        found_seller_section = False
        
        for i, line in enumerate(lines):
            if '销售方' in line or '销 售 方' in line:
                found_seller_section = True
                continue
            
            if found_seller_section:
                # 查找名称行
                if '名称' in line or '名 称' in line:
                    # 尝试从当前行或下一行提取名称
                    match = self.seller_name_pattern.search(line)
                    if match:
                        name = match.group(1).strip()
                        if len(name) >= 2:
                            return name
                    # 检查下一行
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if len(next_line) >= 4 and not any(k in next_line for k in ['纳税', '地址', '开户', '电话']):
                            return next_line
                
                # 如果遇到购买方或其他标志，停止查找
                if '购买方' in line or '购 买 方' in line:
                    break
        
        return ""


def parse_invoice(ocr_items: List[dict], file_name: str = "") -> InvoiceInfo:
    """
    便捷函数：解析发票信息
    
    Args:
        ocr_items: OCR识别结果
        file_name: 文件名
        
    Returns:
        InvoiceInfo对象
    """
    parser = InvoiceParser()
    return parser.parse(ocr_items, file_name)
