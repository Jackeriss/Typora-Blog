import os
import time
import datetime

from bs4 import BeautifulSoup

from src.config import Config

def str2timestamp(time_str):
    if ':' in time_str:
        if '/' in time_str:
            return (time_str.split('/')[0], time.mktime(datetime.datetime.strptime(time_str, '%Y/%m/%d %H:%M:%S').timetuple()))
        return (time_str.split('-')[0], time.mktime(datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timetuple()))
    elif '/' in time_str:
        return (time_str.split('/')[0], time.mktime(datetime.datetime.strptime(time_str, '%Y/%m/%d %H-%M-%S').timetuple()))
    else:
        return (time_str.split('-')[0], time.mktime(datetime.datetime.strptime(time_str, '%Y-%m-%d %H-%M-%S').timetuple()))

def html2template():
    posts = []
    new_posts = os.listdir(os.path.join(Config.ROOT_PATH, 'data/html'))
    post_template_path = os.path.join(Config.ROOT_PATH, 'template/post')
    for template_file_name in os.listdir(post_template_path):
        if template_file_name not in new_posts:
            os.remove(os.path.join(post_template_path, template_file_name))
    for post_file_name in new_posts:
        if '.html' in post_file_name:
            post = {}
            post['title'] = post_file_name.replace('.html', '')
            post['id'] = post['title'].replace(' ', '')
            post_html_path = os.path.join(Config.ROOT_PATH, 'data/html/' + post_file_name)
            with open(post_html_path, 'r') as source_file:
                text = source_file.read()
            soup = BeautifulSoup(text, 'lxml')
            post['year'], post['timestamp'] = str2timestamp(soup.find('p').get_text())
            soup.find('p').decompose()
            post_link = ' ...<a href="/p/%s"> 阅读全文</a>' % post['id']
            abstract = str(soup.find('div', attrs={'class': 'a'}))
            if '</p></div>' in abstract:
                post['abstract'] = abstract.replace('</p></div>', post_link + '</p></div>')
            else:
                post['abstract'] = abstract.replace('</div>', post_link + '</div>')
            if post['abstract'] == str(None):
                post['abstract'] = str(soup.find('p')).replace('</p>', post_link + '</p>')
            template = f"""
                {{% extends "../{Config.ENV}/base.html" %}}
                {{% block description %}}{post['title']}{{% end %}}
                {{% block title %}}{post['title']} - Jackeriss{{% end %}}
                {{% block section %}}
                <div class="postBlock">
                    {str(soup.find('body')).replace('</h2>', '</h2><div class="time"><input type="hidden" value="{{ timestamp }}"/></div>').replace('<a href="', '<a target="_blank" href="')}
                    <div id="gitalk-container"></div>
                </div>
                {{% end %}}
                """
            with open(os.path.join(Config.ROOT_PATH, 'template/post/%s.html' % post['title']), 'w') as template_file:
                template_file.write(template)
            posts.append(post)
    posts.sort(key=lambda x: x['timestamp'], reverse=True)
    return posts

if __name__ == '__main__':
    POSTS = html2template()
    for post in POSTS:
        print(post['id'])
