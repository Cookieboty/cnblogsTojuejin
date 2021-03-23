# coding: utf8
import requests
import os
import argparse
import sys
import json
from lxml import etree
from urllib.parse import urlparse
import logging


parser = argparse.ArgumentParser()
args_dict = {}
list_url_tpl = 'https://www.cnblogs.com/%s/default.html?page=%d'
draft_url = 'https://api.juejin.cn/content_api/v1/article_draft/create_offline'
jj_draft_url_tpl = 'https://juejin.cn/editor/drafts/%s'
cnblog_headers = {}
log_path = './log'

def myget(d, k, v):
    if d.get(k) is None:
        return v
    return d.get(k)

def init_parser():
    parser.description = 'blog move for cnblogs'
    parser.add_argument('-m', '--method', type=str, dest='method', help='使用方式: download下载 upload上传到草稿箱', choices=['upload', 'download'])
    parser.add_argument('-p', '--path', type=str, dest='path', help='博客html下载的路径')
    parser.add_argument('-d', '--dir', type=str, dest='rec_dir', help='制定要上传的博客所在文件夹')
    parser.add_argument('-f', '--file', type=str, dest='file', help='指定上传的博客html')
    parser.add_argument('-u', '--url', type=str, dest='url', help='个人主页地址')
    parser.add_argument('-a', '--article', type=str, dest='article_url', help='单篇文章地址')
    parser.add_argument('--enable_log', dest='enable_log', help='是否输出日志到./log', action='store_true')
    parser.set_defaults(enable_log=False)

def init_log():
    root_logger = logging.getLogger()
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)s  %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
    if myget(args_dict, 'enable_log', False):
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        file_handler =  logging.FileHandler('./log/debug.log')
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
    
def download():
    cookies = json.load(open('cookie.json'))
    headers = {'cookie': cookies.get('cookie_cnblogs', '')}

    dir_path = myget(args_dict, 'path', './cnblogs')
    if dir_path[len(dir_path)-1] == '/':
        dir_path = dir_path[:len(dir_path)-1]
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
    article_url = myget(args_dict, 'article_url', '-1')
    if article_url != '-1':
        logging.info('article_url=%s', article_url)
        try:
            resp = requests.get(article_url, headers=headers)
            if resp.status_code != 200:
                logging.error('fail to get blog \'%s\', resp=%s', article_url, resp)
                return
            tmp_list = article_url.split('/')
            blog_id_str = tmp_list[len(tmp_list)-1]
            with open(dir_path+'/'+blog_id_str, 'w') as f:
                f.write(resp.text)
            logging.info('get blog \'%s\' success.', article_url)
        except Exception as e:
            logging.error('exception raised, fail to get blog \'%s\', exception=%s.', list_url, e)
        finally:
            return

    raw_url = args_dict.get('url')
    rurl = urlparse(raw_url)
    username = (rurl.path.split("/", 1))[1]
    page_no = 1
    while True:
        list_url = list_url_tpl%(username, page_no)
        logging.info('list_url = %s', list_url)
        try:
            resp = requests.get(list_url, headers=headers)
            if resp.status_code != 200:
                break
        except Exception as e:
            logging.error('exception raised, fail to get list \'%s\', exception=%s.', list_url, e)
            return
        html = etree.HTML(resp.text)
        blog_list = html.xpath('//div[@class=\'postTitle\']/a/@href')
        if len(blog_list) == 0:
            break
        for blog_url in blog_list:
            tmp_list = blog_url.split('/')
            blog_id_str = tmp_list[len(tmp_list)-1]
            blog_resp = requests.get(blog_url, headers=headers)
            if resp.status_code != 200:
                logging.error('fail to get blog \'%s\', resp=%s, skip.', blog_url, resp)
                continue
            with open(dir_path+'/'+blog_id_str, 'w') as f:
                f.write(blog_resp.text)
            logging.info('get blog \'%s\' success.', blog_url)
        page_no += 1

def upload_request(headers, content, filename):
    body = {
        "edit_type": 0,
        "origin_type": 2,
        "content": content
    }
    data = json.dumps(body)
    try:
        resp = requests.post(draft_url, data=data, headers=headers)
        if resp.status_code != 200:
            logging.error('fail to upload blog, filename=%s, resp=%s', filename, resp)
            return
        ret = resp.json()
        draft_id = ret.get('data', {}).get('draft_id', '-1')
        logging.info('upload success, filename=%s, jj_draft_id=%s, jj_draft_url=%s', filename, draft_id, jj_draft_url_tpl%draft_id)
    except Exception as e:
        logging.error('exception raised, fail to upload blog, filename=%s, exception=%s', filename, e)
        return
    

def upload():
    cookies = json.load(open('cookie.json'))
    headers = {
        'cookie': cookies.get('cookie_juejin', ''),
        'content-type': 'application/json'
    }
    filename = myget(args_dict, 'file', '-1')
    if filename != '-1':
        logging.info('upload_filename=%s', filename)
        try:
            with open(filename, 'r') as f:
                content = f.read()
                upload_request(headers, content, filename)
            return
        except Exception as e:
            logging.error('exception raised, exception=%s', e)
    
    rec_dir = myget(args_dict, 'rec_dir', '-1')
    if rec_dir != '-1':
        logging.info('upload_dir=%s', filename)
        try:
            g = os.walk(rec_dir)
            for path, dir_list, file_list in g:
                for filename in file_list:
                    if filename.endswith('.html'):
                        filename = os.path.join(path, filename)
                        with open(filename, 'r') as f:
                            content = f.read()
                            upload_request(headers, content, filename)
        except Exception as e:
            logging.error('exception raised, exception=%s', e)
        return


if __name__ == '__main__':
    init_parser()
    args = parser.parse_args()
    args_dict = args.__dict__
    init_log()

    empty_flag = True
    for k, v in args_dict.items():
        if k != 'enable_log' and v is not None:
            empty_flag = False
    if empty_flag:
        parser.print_help()
        exit(0)

    if args_dict.get('method') == 'upload':
        upload()
    else:
        download()
    pass