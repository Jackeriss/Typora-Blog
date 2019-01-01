# Typora-Blog

[![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square)](LICENSE.txt)
[![versions](https://img.shields.io/badge/versions%20-%20%201.0.0-blue.svg?style=flat-square)]()  

Write blog using Typora! [demo](//www.jackeriss.com)

## Introduction
Typora-Blog is a simple but special blog program, Its biggest characteristic is post editing will be done locally, and use a specific Markdown editor —— [Typora](http://typora.io)

### Features
1. *Less is more*. It only keeps the most frequently used features of a blog program. So, no post type, no tags and no searching. If you really want these features, please add them yourself.
2. No DB required, which makes it easy to deploy and manage.
3. Friendly for extensions. Since it's not a static blog, you can realize more features you want.

## Usage
### Deploy
GitHub provides a Webhook, you can use it for automatic deployment.

### Customization
1. This blog program does not provide blog name, logo and other configurations in `/config.py`, please directly modify the template file `/app/templates/base.html`, if want to change the appearance of the blog, please edit `/app/static/CSS/style.css`.
2. The program can accept two arguments, use `--help` for more information.

### Convention over configuration
1. Write your post with Typora.
2. Use `h2` at title.
3. Write down the current time in the following format at the first paragraph: `YY-mm-dd HH-MM-S` `YY-mm-dd HH:MM:SS` `YY/mm/dd HH-MM-SS` `YY/mm/dd HH:MM:SS`(Chinese users can use Sogou typing `sj` to input the current time in format quickly.)
4. Wrap the abstract using `<div id="a"></div>`, or the first `p` except the time paragraph will be the abstract.
5. Export it with style and put it under `/posts`.
6. The file name should be exactly the same with the title of your post, and it should end up with `.html`.
7. add all -> commit -> push
8. You should keep the `.md` files to make it easy for you to reedit your posts.

## License
MIT © [Jackeriss](//www.jackeriss.com)
