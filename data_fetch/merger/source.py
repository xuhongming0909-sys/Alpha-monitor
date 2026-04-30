#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收购合并套利机会挖掘脚本（优化版）
从巨潮资讯获取公告信息，筛选收购、合并、重组等套利机会
优化：并发搜索、并发获取股价、精简搜索范围
"""

import json
import sys
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.config.script_config import get_config

_CONFIG = get_config()
_MERGER_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("merger") or {})
_ANNOUNCEMENT_TIMEOUT = max(1, int(_MERGER_CONFIG.get("announcement_timeout_seconds") or 5))
_QUOTE_TIMEOUT = max(1, int(_MERGER_CONFIG.get("quote_timeout_seconds") or 15))

# 搜索关键词配置
SEARCH_KEYWORDS = [
    '要约收购',
    '吸收合并', 
    '协议收购',
    '重大资产重组',
    '私有化',
]

# 核心公告关键词（用于识别核心交易文件）
CORE_KEYWORDS = [
    '要约收购报告书',
    '要约收购提示性公告',
    '收购报告书',
    '吸收合并报告书',
    '重大资产重组报告书',
    '重组报告书',
    'merger_report书',
    '合并报告书',
]

# 子公司/孙公司内部重组关键词（这类公告无套利价值）
SUBSIDIARY_KEYWORDS = [
    '全资子公司',
    '控股子公司',
    '全资孙公司',
    '控股孙公司',
    '子公司之间吸收合并',
    '孙公司之间吸收合并',
    '吸收合并其全资',
    '吸收合并其控股',
    '吸收合并全资子公司',
    '吸收合并全资孙公司',
    '吸收合并控股子公司',
    '吸收合并控股孙公司',
]

# 非上市公司主体交易关键词（交易主体不是上市公司本身）
NON_COMPANY_KEYWORDS = [
    '控股股东拟被吸收合并',
    '间接股东拟被吸收合并',
    '控股股东被吸收合并',
    '间接股东被吸收合并',
    '控股股东权益变动',
    '间接股东权益变动',
    '关于控股股东拟被吸收合并',
    '关于间接股东拟被吸收合并',
    '控股股东一致行动人被吸收合并',
    '关于新增间接控股股东',
    '新增间接控股股东',
    '关于控股股东一致行动人',
    '股东被吸收合并',
    '股东拟被吸收合并',
    '持股5%以上股东被吸收合并',
    '关于公司股东拟被吸收合并',
    '关于公司股东被吸收合并',
    '股东被吸收合并完成股权过户登记',
]

# 已结束/已终止交易关键词（这类公告已无套利价值）
ENDED_TRANSACTION_KEYWORDS = [
    # 单词排除
    '终止',
    '交割',
    '上市',
    
    # 终止类
    '终止公告',
    '终止实施',
    '终止本次',
    '终止收购',
    '终止合并',
    '终止重组',
    '终止交易',
    '终止筹划',
    '决定终止',
    '申请终止',
    '自动终止',
    '提前终止',
    '不再推进',
    '不再继续',
    '中止',
    
    # 撤回类
    '撤回申请',
    '撤回材料',
    '撤回文件',
    '撤回申报',
    '申请撤回',
    '主动撤回',
    
    # 审核结果类
    '未获通过',
    '被否决',
    '审核未通过',
    '不予核准',
    '不予批准',
    '未获核准',
    '未获批准',
    '被驳回',
    
    # 结果公告类
    '收购结果',
    '合并结果',
    '重组结果',
    '要约收购结果',
    '要约收购完成',
    '吸收合并完成',
    '吸收合并结果',
    
    # 要约结束类
    '要约收购期限届满',
    '要约收购期满',
    '要约期届满',
    '要约期限届满',
    '竞争要约',
    '要约清算',
    '要约交收',
    '要约结束',
    
    # 过户完成类
    '过户完成',
    '股份过户',
    '股权过户',
    '过户登记',
    '完成过户',
    
    # 免于/豁免类
    '免于',
    '豁免',
    '免于要约',
    '豁免要约',
    '免于履行',
    '豁免履行',
    '免于发出',
    '豁免发出',
    
    # 其他结束类
    '未能完成',
    '无法完成',
    '不再实施',
    '取消实施',
    '放弃实施',
]

class MergerArbitrageScraper:
    """收购合并套利数据获取器（优化版）"""
    
    def __init__(self):
        self.base_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://www.cninfo.com.cn/',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.stock_price_cache = {}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_stock_price(self, code: str) -> Optional[Dict[str, Any]]:
        """获取股票实时价格"""
        if code in self.stock_price_cache:
            return self.stock_price_cache[code]
        
        # 判断市场
        if code.startswith('6'):
            market = 'sh'
        else:
            market = 'sz'
        
        query_code = f"{market}{code}"
        url = f"https://web.sqt.gtimg.cn/q={query_code}"
        
        try:
            response = self.session.get(url, timeout=_ANNOUNCEMENT_TIMEOUT)
            text = response.content.decode('gbk')
            
            match = re.match(r'v_([^=]+)="(.+)"', text.strip())
            if match:
                parts = match.group(2).split('~')
                if len(parts) >= 4:
                    name = parts[1]
                    try:
                        price = float(parts[3]) if parts[3] else 0
                    except:
                        price = 0
                    
                    result = {
                        'code': code,
                        'name': name,
                        'price': price,
                        'market': market.upper(),
                    }
                    self.stock_price_cache[code] = result
                    return result
        except Exception as e:
            print(f'获取股价失败 {code}: {e}', file=sys.stderr)
        
        return None
    
    def batch_get_stock_prices(self, codes: List[str]) -> Dict[str, Dict]:
        """批量获取股价（并发）"""
        results = {}
        unique_codes = list(set(codes))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_code = {
                executor.submit(self.get_stock_price, code): code 
                for code in unique_codes
            }
            for future in as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result()
                    if result:
                        results[code] = result
                except Exception as e:
                    print(f'批量获取股价异常 {code}: {e}', file=sys.stderr)
        
        return results
    
    def search_announcements(self, keyword: str, days: int = 90) -> List[Dict[str, Any]]:
        """搜索公告（获取所有结果）"""
        results = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 搜索所有页面
        page_num = 1
        while True:
            data = {
                'pageNum': page_num,
                'pageSize': 30,
                'column': 'szse',
                'tabName': 'fulltext',
                'plate': '',
                'stock': '',
                'searchkey': keyword,
                'secid': '',
                'category': '',
                'trade': '',
                'seDate': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
                'sortName': 'time',
                'sortType': 'desc',
                'isHLtitle': 'true',
            }
            
            try:
                response = self.session.post(
                    self.base_url, 
                    data=data, 
                    timeout=_QUOTE_TIMEOUT
                )
                result = response.json()
                
                announcements = result.get('announcements', [])
                if not announcements:
                    # 没有更多结果
                    break
                
                for ann in announcements:
                    # 清理标题中的高亮标签
                    title = ann.get('announcementTitle', '')
                    title = re.sub(r'</?em>', '', title)
                    
                    results.append({
                        'announcementId': ann.get('announcementId', ''),
                        'secCode': ann.get('secCode', ''),
                        'secName': ann.get('secName', ''),
                        'orgId': ann.get('orgId', ''),
                        'title': title,
                        'announcementTime': ann.get('announcementTime', 0),
                        'pdfUrl': f"http://static.cninfo.com.cn/{ann.get('adjunctUrl', '')}",
                        'announcementUrl': f"http://www.cninfo.com.cn/new/disclosure/stock?stockCode={ann.get('secCode', '')}&announcementId={ann.get('announcementId', '')}&orgId={ann.get('orgId', '')}",
                        'searchKeyword': keyword,
                    })
                
                page_num += 1
                # 短暂延迟避免请求过快
                import time
                time.sleep(0.15)
                
            except Exception as e:
                print(f'搜索公告失败 {keyword} 第{page_num}页: {e}', file=sys.stderr)
                break
        
        print(f'  搜索 {keyword} 共获取 {len(results)} 条公告', file=sys.stderr)
        return results
    
    def search_all_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """并发搜索所有关键词"""
        all_announcements = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_keyword = {
                executor.submit(self.search_announcements, kw): kw 
                for kw in keywords
            }
            
            for future in as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                try:
                    results = future.result()
                    all_announcements.extend(results)
                    print(f'搜索关键词: {keyword} 完成', file=sys.stderr)
                except Exception as e:
                    print(f'搜索关键词 {keyword} 异常: {e}', file=sys.stderr)
        
        return all_announcements
    
    def is_core_announcement(self, title: str) -> tuple:
        """判断是否为核心公告文件"""
        # 排除子公司/孙公司内部重组公告（无套利价值）
        for subsidiary_kw in SUBSIDIARY_KEYWORDS:
            if subsidiary_kw in title:
                return False, None
        
        # 排除非上市公司主体交易（交易主体不是上市公司本身）
        for non_company_kw in NON_COMPANY_KEYWORDS:
            if non_company_kw in title:
                return False, None
        
        # 排除已结束/已终止的交易（无套利价值）
        for ended_kw in ENDED_TRANSACTION_KEYWORDS:
            if ended_kw in title:
                return False, None
        
        # 检查是否包含核心关键词
        for core_kw in CORE_KEYWORDS:
            if core_kw in title:
                # 识别交易类型
                if '要约收购' in core_kw or '要约收购' in title:
                    deal_type = '要约收购'
                elif '吸收合并' in core_kw or '吸收合并' in title:
                    deal_type = '吸收合并'
                elif '重组' in core_kw or '重组' in title:
                    deal_type = '重组'
                elif '合并' in core_kw:
                    deal_type = '吸收合并'
                else:
                    deal_type = '其他'
                
                return True, deal_type
        
        # 如果标题直接包含关键词
        for kw in SEARCH_KEYWORDS:
            if kw in title:
                if '要约收购' in kw:
                    return True, '要约收购'
                elif '吸收合并' in kw:
                    return True, '吸收合并'
                elif '协议收购' in kw:
                    return True, '协议收购'
                elif '重组' in kw:
                    return True, '重组'
                elif '私有化' in kw:
                    return True, '私有化'
        
        return False, None
    
    def parse_deal_price(self, title: str) -> Optional[float]:
        """从标题中解析交易价格"""
        patterns = [
            r'(\d+\.?\d*)\s*元/股',
            r'(\d+\.?\d*)\s*元每股',
            r'要约价[为是]?\s*(\d+\.?\d*)\s*元',
            r'收购价[为是]?\s*(\d+\.?\d*)\s*元',
            r'价格[为是]?\s*(\d+\.?\d*)\s*元',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        
        return None
    
    def deduplicate_announcements(self, announcements: List[Dict]) -> List[Dict]:
        """公告去重（按股票代码分组，保留每个股票最新的核心公告）"""
        stock_announcements = {}
        
        for ann in announcements:
            code = ann['secCode']
            
            if code not in stock_announcements:
                stock_announcements[code] = ann
            elif ann.get('isCore', False) and not stock_announcements[code].get('isCore', False):
                stock_announcements[code] = ann
            elif ann.get('isCore', False) and stock_announcements[code].get('isCore', False):
                if ann['announcementTime'] > stock_announcements[code]['announcementTime']:
                    stock_announcements[code] = ann
        
        return list(stock_announcements.values())
    
    def run(self) -> Dict[str, Any]:
        """执行数据获取（优化版）"""
        print(f'开始获取公告数据，搜索关键词: {SEARCH_KEYWORDS}', file=sys.stderr)
        
        # 并发搜索所有关键词
        all_announcements = self.search_all_keywords(SEARCH_KEYWORDS)
        
        # 去重（按announcementId）
        seen_ids = set()
        unique_announcements = []
        for ann in all_announcements:
            if ann['announcementId'] not in seen_ids:
                seen_ids.add(ann['announcementId'])
                unique_announcements.append(ann)
        
        print(f'去重后共 {len(unique_announcements)} 条公告', file=sys.stderr)
        
        # 筛选核心公告
        results = []
        codes_need_price = []
        
        for ann in unique_announcements:
            is_core, deal_type = self.is_core_announcement(ann['title'])
            ann['isCore'] = is_core
            ann['dealType'] = deal_type
            
            # 检查是否为子公司内部重组
            is_subsidiary_deal = any(kw in ann['title'] for kw in SUBSIDIARY_KEYWORDS)
            
            # 检查是否为非上市公司主体交易
            is_non_company_deal = any(kw in ann['title'] for kw in NON_COMPANY_KEYWORDS)
            
            # 检查是否为已结束/已终止的交易
            is_ended_deal = any(kw in ann['title'] for kw in ENDED_TRANSACTION_KEYWORDS)
            
            if (is_core or any(kw in ann['title'] for kw in SEARCH_KEYWORDS)) and not is_subsidiary_deal and not is_non_company_deal and not is_ended_deal:
                # 解析交易价格
                ann['offerPrice'] = self.parse_deal_price(ann['title'])
                codes_need_price.append(ann['secCode'])
                results.append(ann)
        
        # 批量获取股价（并发）
        print(f'批量获取 {len(codes_need_price)} 只股票价格...', file=sys.stderr)
        stock_prices = self.batch_get_stock_prices(codes_need_price)
        
        # 填充股价信息
        for ann in results:
            code = ann['secCode']
            if code in stock_prices:
                ann['stockPrice'] = stock_prices[code]['price']
                ann['stockName'] = stock_prices[code]['name']
            else:
                ann['stockPrice'] = None
            
            # 格式化公告时间
            if ann['announcementTime']:
                ann['announcementDate'] = datetime.fromtimestamp(
                    ann['announcementTime'] / 1000
                ).strftime('%Y-%m-%d')
            else:
                ann['announcementDate'] = ''
        
        # 再次去重（按股票代码）
        results = self.deduplicate_announcements(results)
        
        # 按公告时间排序
        results.sort(key=lambda x: x.get('announcementTime', 0), reverse=True)
        
        print(f'最终筛选出 {len(results)} 条套利机会', file=sys.stderr)
        
        return {
            'success': True,
            'data': results,
            'total': len(results),
            'updateTime': datetime.now().isoformat(),
            'keywords': SEARCH_KEYWORDS,
        }


def main():
    """主函数"""
    scraper = MergerArbitrageScraper()
    result = scraper.run()
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()

