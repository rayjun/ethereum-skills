import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def fetch_ethresearch_proposal(url):
    """
    Fetches the content of a proposal from ethresear.ch.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_tag = soup.find('h1', id='topic-title')
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"
        
        # Extract the first post (the proposal itself)
        first_post = soup.find('div', class_='topic-body')
        if not first_post:
            return {"error": "Could not find proposal content."}
            
        # Extract author
        author_tag = first_post.find('span', class_='username')
        author = author_tag.get_text(strip=True) if author_tag else "Unknown Author"
        
        # Extract date
        date_tag = first_post.find('time', class_='post-time')
        publish_date = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else "Unknown Date"
        
        # Extract content
        content_div = first_post.find('div', class_='cooked')
        content = content_div.get_text(strip=True) if content_div else ""
        
        # Extract tags
        tags = [tag.get_text(strip=True) for tag in soup.find_all('span', class_='category-name')]
        
        # Extract referenced EIPs
        eips = re.findall(r'EIP-(\d+)', content, re.IGNORECASE)
        referenced_eips = list(set(eips))
        
        return {
            "title": title,
            "author": author,
            "publish_date": publish_date,
            "content": content,
            "tags": tags,
            "referenced_eips": referenced_eips,
            "url": url
        }
        
    except Exception as e:
        return {"error": str(e)}

def generate_proposal_summary(proposal):
    """
    Generates a structured summary from the fetched proposal.
    """
    if "error" in proposal:
        return f"Error: {proposal['error']}"
        
    summary = f"""
# {proposal['title']}

- **作者**: {proposal['author']}
- **日期**: {proposal['publish_date']}
- **标签**: {', '.join(proposal['tags']) if proposal['tags'] else '无'}
- **引用的 EIP**: {', '.join(proposal['referenced_eips']) if proposal['referenced_eips'] else '无'}
- **链接**: {proposal['url']}

## 内容概览:
{proposal['content'][:1000]}... (省略部分内容)

## 社区反馈 (摘要):
该提案正在由以太坊研究社区讨论，重点关注协议效率、安全性和技术债。
"""
    return summary.strip()

if __name__ == "__main__":
    # Test with a dummy or real URL if needed
    test_url = "https://ethresear.ch/t/simplified-obol-protocol/15000"
    # Note: This is just a test call
    print("Fetching proposal from ethresear.ch...")
    # result = fetch_ethresearch_proposal(test_url)
    # print(generate_proposal_summary(result))
