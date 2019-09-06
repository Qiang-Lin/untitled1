import requests
import os

# def getHTMLText(url):
#     try:
#         r = requests.get(url)
#         r.raise_for_status()
#         print(r.status_code)
#         with open(path, 'wb') as f:
#             f.write(r.content)
#         return r.text
#     except:
#         return "error"


if __name__ == "__main__":
    root = "D://pics//"
    url = "http://image.nationalgeographic.com.cn/2017/0211/20170211061910157.jpg"
    path = os.path.join(root, url.split('/')[-1])
    try:
        if not os.path.exists(root):
            os.mkdir(root)
        if not os.path.exists(path):
            r = requests.get(url)
            with open(path, 'wb') as f:
                f.write(r.content)
                f.close()
                print('文件保存成功')
        else:
            print("文件已存在")
    except:
        print("爬取失败")
