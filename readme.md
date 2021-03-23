# cnblogs搬家命令行工具demo
## 使用
需要python3环境，请在cookie.json中补充博客园与掘金的cookie<br/>
使用python3 main.py -h 查看使用说明
## 示例
请先在cookie.json中替换cookie_cnblogs与cookie_juejin为自己在对应站点上的cookie<br/>
```shell
请自行替换user_name与blog_id
// 下载单篇文章到默认目录'./cnblogs' 并输出日志到'./log'
python3 main.py -m download -a https://www.cnblogs.com/{{user_name}}/p/{{blog_id}}.html --enable_log 

// 下载用户所有文章到目录'/Users/cnblogs_t'
python3 main.py -m download -u https://www.cnblogs.com/{{username}} -p /Users/cnblogs_t

// 上传单篇文章到掘金草稿箱
python3 main.py -m upload -f ./cnblogs/{{blog_id}}.html

// 上传'./test_blogs'下所有的html文件到掘金草稿箱
python3 main.py -m upload -d ./test_blogs
```