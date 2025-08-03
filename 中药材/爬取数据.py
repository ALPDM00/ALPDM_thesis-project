import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import csv
from fake_useragent import UserAgent

def get_random_headers():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }
    return headers

def decode_content(response):
    """尝试使用不同的编码方式解码内容"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'iso-8859-1']
    content = response.content
    
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # 如果所有编码都失败，尝试使用apparent_encoding
    try:
        return content.decode(response.apparent_encoding)
    except UnicodeDecodeError:
        raise Exception("无法解码网页内容")

def get_medicine_details(url):
    # 随机延迟1-3秒
    time.sleep(random.uniform(1, 3))
    
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()
        
        # 使用新的解码函数
        html_content = decode_content(response)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 初始化数据字典
        medicine_data = {
            '中药名': '',
            '别名': '',
            '英文名': '',
            '场地分布': '',
            '采收加工': '',
            '药材性状': '',
            '性味归经': '',
            '功效与作用': '',
            '使用禁忌': ''
        }
        
        # 获取所有段落
        paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text.startswith('【中药名】'):
                medicine_data['中药名'] = text.replace('【中药名】', '').strip()
            elif text.startswith('【别名】'):
                medicine_data['别名'] = text.replace('【别名】', '').strip()
            elif text.startswith('【英文名】'):
                medicine_data['英文名'] = text.replace('【英文名】', '').strip()
            elif text.startswith('【产地分布】'):
                medicine_data['场地分布'] = text.replace('【产地分布】', '').strip()
            elif text.startswith('【采收加工】'):
                medicine_data['采收加工'] = text.replace('【采收加工】', '').strip()
            elif text.startswith('【药材性状】'):
                medicine_data['药材性状'] = text.replace('【药材性状】', '').strip()
            elif text.startswith('【性味归经】'):
                medicine_data['性味归经'] = text.replace('【性味归经】', '').strip()
            elif text.startswith('【功效与作用】'):
                medicine_data['功效与作用'] = text.replace('【功效与作用】', '').strip()
            elif text.startswith('【使用禁忌】'):
                medicine_data['使用禁忌'] = text.replace('【使用禁忌】', '').strip()
        
        return medicine_data
    
    except Exception as e:
        print(f"Error fetching details from {url}: {str(e)}")
        return None

def get_medicine_links(page_url):
    try:
        response = requests.get(page_url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()
        
        # 使用新的解码函数
        html_content = decode_content(response)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 获取所有药材链接
        medicine_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and '/name/' in href and href != '/name/':
                if not href.startswith('http'):
                    href = 'http://www.zhongyoo.com' + href
                medicine_links.append(href)
        
        return medicine_links
    
    except Exception as e:
        print(f"Error fetching page {page_url}: {str(e)}")
        return []

def main():
    base_url = 'http://www.zhongyoo.com/name/'
    first_page_links = get_medicine_links(base_url)
    
    print(f"找到 {len(first_page_links)} 个药材链接")
    
    # 创建一个列表存储所有数据
    all_medicines_data = []
    
    # 遍历第一页的所有链接
    for i, link in enumerate(first_page_links, 1):
        print(f"正在获取第 {i}/{len(first_page_links)} 个药材数据: {link}")
        medicine_data = get_medicine_details(link)
        if medicine_data:
            all_medicines_data.append(medicine_data)
    
    # 将数据保存为CSV文件
    if all_medicines_data:
        df = pd.DataFrame(all_medicines_data)
        df.to_csv('中药材数据.csv', index=False, encoding='utf-8-sig')
        print(f"成功获取 {len(all_medicines_data)} 个药材数据，已保存到 中药材数据.csv")
    else:
        print("未获取到任何数据")

if __name__ == "__main__":
    main()
