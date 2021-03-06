import os
from functools import lru_cache

from bs4 import BeautifulSoup

from app.constant import constant
from app.util.config_util import config
from app.util.time_util import time_str2timestamp


class PostService(object):
    @classmethod
    @lru_cache(maxsize=None)
    def gen_posts(cls):
        posts = []
        new_posts = os.listdir(os.path.join(config.base_dir, "data/html"))
        post_template_path = os.path.join(config.base_dir, "template/post")
        for template_file_name in os.listdir(post_template_path):
            os.remove(os.path.join(post_template_path, template_file_name))
        for post_file_name in new_posts:
            if ".html" in post_file_name:
                post = {}
                post["title"] = post_file_name.replace(".html", "")
                post["id"] = post["title"].replace(" ", "")
                post_html_path = os.path.join(
                    config.base_dir, "data/html/" + post_file_name
                )
                with open(post_html_path, "r") as source_file:
                    text = source_file.read()
                text = text.replace("<a href=", "<a target='_blank' href=")
                soup = BeautifulSoup(text, "lxml")
                post["year"], post["timestamp"] = time_str2timestamp(
                    soup.find("p").get_text()
                )
                soup.find("p").decompose()
                post_link = ' ...<a href="/post/%s"> 阅读全文</a>' % post["id"]
                abstract = str(soup.find("div", attrs={"class": "a"}))
                if "</p></div>" in abstract:
                    post["abstract"] = abstract.replace(
                        "</p></div>", f"{post_link}</p></div>"
                    )
                else:
                    post["abstract"] = abstract.replace("</div>", post_link + "</div>")
                if post["abstract"] == str(None):
                    abstract = str(soup.find("p"))
                    post["abstract"] = (
                        abstract.replace("</p>", f"<p>{post_link}</p></p>")
                        if "<img" in abstract
                        else abstract.replace("</p>", f"{post_link}</p>")
                    )
                template = f"""
                    {{% extends "..{"/dist" if config.env != "dev" else ""}/base.html" %}}
                    {{% block description %}}{post['title']}{{% end %}}
                    {{% block title %}}{post['title']} - Jackeriss{{% end %}}
                    {{% block section %}}
                    <div class="postBlock">
                        {str(soup.find('body')).replace(
                            '</h2>',
                            '</h2><div class="time"><input type="hidden" value="{{ timestamp }}"/></div>'
                        )}
                        <div id="gitalk-container"></div>
                    </div>
                    {{% end %}}
                    """
                with open(
                    os.path.join(
                        config.base_dir, "template/post/%s.html" % post["title"]
                    ),
                    "w",
                ) as template_file:
                    template_file.write(template)
                posts.append(post)
        posts.sort(key=lambda x: x["timestamp"], reverse=True)
        return posts

    @classmethod
    def get_total_page(cls):
        total_page = int(
            (len(cls.gen_posts()) + constant.PAGE_LIMIT - 1) / constant.PAGE_LIMIT
        )
        return total_page

    @classmethod
    def get_posts(cls, page=None):
        posts = cls.gen_posts()
        if page:
            total_page = cls.get_total_page()
            if page < total_page:
                posts = posts[
                    (page - 1) * constant.PAGE_LIMIT : page * constant.PAGE_LIMIT
                ]
            elif page == total_page:
                posts = posts[(page - 1) * constant.PAGE_LIMIT : len(posts)]
        return posts

    @classmethod
    def get_post(cls, post_id=None):
        posts = cls.gen_posts()
        for post in posts:
            if post_id == post["id"]:
                return post
        return None
