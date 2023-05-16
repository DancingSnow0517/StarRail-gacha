from lanzou.api import LanZouCloud

COOKIE_STR = "_uab_collina=166567064126113206383603; ylogin=1523461; PHPSESSID=as0jk5qba8934a0ehjr523quvfa1sfgd; phpdisk_info=UmdVYlY2DTJVYwFnWzBTAFs6UWRbC1cxV2xSNFVrATpWYVJnA2ZXaQIyB2FdDlVqUzFRMQFoBmhUZwJlUjIEZFJuVTNWNw01VWEBNFs0U2xbPFFmWzVXMFdmUjVVZgE0VjRSZQNnV24CZQcxXTRVBlMyUWsBbgZpVG4CYVJjBDFSZFVlVjI=; uag=a97525abb31f6535141e6d05aac8c5a2; folder_id_c=7558561"


def upload_callback(file_name, total_size, now_size):
    print(f"Uploading {file_name}: {now_size}/{total_size}")


if __name__ == '__main__':
    cookie = {}
    for c in COOKIE_STR.split("; "):
        print(c)
        k, v = c.split("=", 1)
        cookie[k] = v

    print(cookie)
    lanzou = LanZouCloud()
    if lanzou.login_by_cookie(cookie) != LanZouCloud.SUCCESS:
        print("登录失败")
        exit(1)
    print("登录成功")

    print(lanzou.upload_file("build/StarRail-Gacha-Exporter-0.4.3路径修复.zip", 7558561, callback=upload_callback))
