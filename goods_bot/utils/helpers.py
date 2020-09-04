# -*- coding: utf-8 -*-
"""
工具包
"""
import base64
import datetime
import hashlib
import json
import os
import re
import sys
import http.cookiejar as cookielib
import requests
import time

import lxml.html.clean as clean

from lxml import html

from scrapy.utils.project import get_project_settings
from w3lib.util import to_unicode

from six.moves.urllib.parse import urljoin, urlparse

# reload(sys)
# sys.setdefaultencoding('utf-8')

class Time(object):
    """
    时间操作类
    """
    @staticmethod
    def datetime2timestamp(date_time, convert_to_utc=False):
        ''' Converts a datetime object to UNIX timestamp in milliseconds. '''
        epoch = datetime.datetime.utcfromtimestamp(0)
        if isinstance(date_time, datetime.datetime):
            # 是否转化为UTC时间
            if convert_to_utc:
                date_time = date_time + datetime.timedelta(hours=-8) # 中国默认时区
            timestamp = datetime.timedelta.total_seconds(date_time - epoch)
            return int(timestamp)
        return date_time

    @staticmethod
    def timestamp2datetime(timestamp, convert_to_local=False):
        ''' Converts UNIX timestamp to a datetime object. '''
        if isinstance(timestamp, (int, float)):
            try:
                # date_time = datetime.datetime.utcfromtimestamp(timestamp)
                date_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)
                # 转化为中国本地时间
                if convert_to_local:
                    date_time = date_time + datetime.timedelta(hours=8) # 中国默认时区

                return date_time
            except:
                pass

        return datetime.datetime(2199, 1, 1)


    @staticmethod
    def timestamp_utc_now():
        """
        取得当前UTC时间戳
        """
        return Time.datetime2timestamp(datetime.datetime.utcnow())

    @staticmethod
    def timestamp_now():
        """
        取得当前时间戳
        """
        return Time.datetime2timestamp(datetime.datetime.now())


class JSON(object):
    """
    JSON操作类
    """
    @staticmethod
    def dumps(obj, **kwargs):
        """
        将对象转为JSON字符串,(支持日期格式)
        """
        default_params = {
            "default" : JSON._date_handler,
        }
        merged_params = dict(kwargs, **default_params)
        return json.dumps(obj, **merged_params)

    @staticmethod
    def dump(obj, fp, **kwargs):
        """
        将对象转为JSON字符串,(支持日期格式)
        """
        default_params = {
            "default" : JSON._date_handler,
        }
        merged_params = dict(kwargs, **default_params)
        return json.dump(obj, fp, **merged_params)

    @staticmethod
    def loads(s, **kwargs):
        """
        加载JSON字符串
        """
        default_params = {
            # "default" : JSON._date_handler,
        }
        merged_params = dict(kwargs, **default_params)
        return json.loads(s, **merged_params)

    @staticmethod
    def load(f, **kwargs):
        """
        加载JSON字符串
        """
        default_params = {
            # "default" : JSON._date_handler,
        }
        merged_params = dict(kwargs, **default_params)
        return json.load(f, **merged_params)

    @staticmethod
    def _date_handler(obj):
        """
        print json.dumps(data, default=Time.date_handler)
        """
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError


class File(object):
    """
    文件操作类
    """
    @staticmethod
    def save_to(msg, filename):
        """
        将字符串保存到文件中
        """
        File.check_and_make_dir(os.path.dirname(filename))

        with open(filename, "w") as text_file:
            text_file.write(msg)
            text_file.close()

    @staticmethod
    def append_lines(msglist, filename):
        """
        将字符串数组添加到文件中
        """
        File.check_and_make_dir(os.path.dirname(filename))

        with open(filename, "a") as text_file:
            text_file.writelines("%s\n" % msg for msg in msglist)
            text_file.close()

    @staticmethod
    def append_line(msg, filename):
        """
        将字符串添加到文件中
        """
        File.check_and_make_dir(os.path.dirname(filename))

        with open(filename, "a") as text_file:
            text_file.write("%s\n" % msg)
            text_file.close()


    @staticmethod
    def check_and_make_dir(dirname):
        """
        创建文件夹
        """
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)


    # download couter
    download_count = 0
    startTime = time.perf_counter()
    # estimate 预算，下载estimate个文件后，计算下载速度,如果此参数为0则不作统计
    estimate = 10

    @staticmethod
    def download(url, filename, overwrite=False):
        """
        下载图片
        """
        result = ''
        if not overwrite and os.path.exists(filename):
            return filename

        r = requests.get(url)
        if r.status_code == 200:
            File.check_and_make_dir(os.path.dirname(filename))
            with open(filename, "wb") as f:
                f.write(r.content)
                f.close()
                print('download success:{}'.format(filename))
                result = filename
        else:
            print('download error:{}'.format(filename))
            result = None

        if File.estimate:
            if File.download_count == File.estimate:
                endTime = time.perf_counter()
                print(' at {} rows/min'.format(int(File.estimate * 60/(endTime - File.startTime))))
                File.download_count = 0
                File.startTime = endTime
            else:
                File.download_count += 1

        return result

    @staticmethod
    def save_to_b64(str_b64, filename):
        """
        将Base64的字符串转成二进制形式,保存到文件中
        """
        bin_bytes = base64.b64decode(str_b64)

        File.check_and_make_dir(os.path.dirname(filename))

        with open(filename, 'wb') as bfile:
            bfile.write(bin_bytes)
            bfile.close()

    @staticmethod
    def load_src(filename):
        """
        加载lua源码

        @filename lua源文件名

        从setting.py中设定的SRC_DIR文件夹中加载指定的lua源代码文件

        """
        ret = ""
        config = get_project_settings()
        luadir = config.get("SRC_DIR")
        fullpath = luadir + "/" + filename
        with open(fullpath, "rt") as luafile:
            ret = luafile.read()
            luafile.close()
        return ret

    @staticmethod
    def load_cookies(cookies_file):
        """
        从设定文件中的PROJECT_ROOT/cookies中加载cookies文件

        文件格式:

        <name1>=<value1>; <name2>=<value2>
        pgv_pvi=6278713344; RK=IN161eyfcC;
        """
        config = get_project_settings()
        prj_dir = config.get("PROJECT_ROOT")
        fullpath = prj_dir + "/cookies/" + cookies_file

        with open(fullpath, "rt") as cf:
            cookies_str = cf.readline()
            cf.close()

            regex = r"\s*([^=;]+)=([^;]+)"
            matches = re.finditer(regex, cookies_str, re.IGNORECASE | re.UNICODE | re.DOTALL)
            cookies = {}
            for match in matches:
                cookies[match.group(1)] = match.group(2)

            return cookies
        return {}

    @staticmethod
    def load_cookies_text(cookies_file):
        """
        从设定文件中的PROJECT_ROOT/cookies中加载cookies文件

        @see http://stackoverflow.com/questions/14742899/using-cookies-txt-file-with-python-requests
        """
        config = get_project_settings()
        prj_dir = config.get("PROJECT_ROOT")
        fullpath = prj_dir + "/cookies/" + cookies_file
        if not os.path.exists(fullpath):
            return []

        cookiejar = cookielib.MozillaCookieJar(fullpath)
        cookiejar.load()

        cookies = []
        for cookie in cookiejar:
            # set cookie expire date to 14 days from now
            new_cookie = {
                'domain':cookie.domain,
                'value': cookie.value,
                'name' : cookie.name,
                'path' : cookie.path,
                'httpOnly': False,
                'expires': Time.timestamp2datetime(cookie.expires).isoformat(),
                'secure': cookie.secure
            }
            cookies.append(new_cookie)

        return cookies

    @staticmethod
    def load_cookies_json(cookies_file):
        """
        加载json形式的cookies
        """
        config = get_project_settings()
        prj_dir = config.get("PROJECT_ROOT")
        fullpath = prj_dir + "/cookies/" + cookies_file

        try:
            if os.path.exists(fullpath):
                fhandle = open(fullpath)
                result = json.load(fhandle)
                fhandle.close()
                return result
        except:
            print("Load cookies file:{} FAILED".format(cookies_file))

        return {}

    @staticmethod
    def save_cookies_json(cookies, cookies_file):
        """
        将cookies保存为json格式
        """
        config = get_project_settings()
        prj_dir = config.get("PROJECT_ROOT")
        fullpath = prj_dir + "/cookies/" + cookies_file

        with open(fullpath, 'w') as outfile:
            JSON.dump(cookies, outfile)

class Helper(object):
    """
    辅助类
    """


    @staticmethod
    def dict2list(dict_src, key_list):
        """
        dict转list
        """
        tlist = []
        for key in key_list:
            tlist.append(dict_src[key])
        return tlist

    @staticmethod
    def get(thedict, key, default=None):
        """
        获取dict中的key值, 如果不存在,返回default
        """
        if key in thedict:
            return thedict[key]
        else:
            return default

    @staticmethod
    def make_origin(userid, spider):
        """
        来源:=userid@爬虫名
        """
        return "{}@{}".format(userid, spider.name)

    @staticmethod
    def md5(*args):
        """
        将参数组合并生成md5

        示例:

        Helper.md5("abc", "def")
        """
        md5 = hashlib.md5()
        for value in args:
            if value:
                if isinstance(value, str):
                    md5.update(value.encode('utf8'))
                else:
                    md5.update(value)
        return md5.hexdigest()


    @staticmethod
    def re_group(test_str, regex, i):
        """
        取出正则表达式中指定的值
        """
        matches = re.search(regex, test_str, re.DOTALL | re.UNICODE)

        if matches and i <= len(matches.groups()):
            return matches.group(i)

    @staticmethod
    def re_groups(test_str, regex):
        """
        取出正则表达式中匹配到项目元祖
        例：
            def parse_breadcrumb(breadcrumb):
                r = {}
                g = Helper.re_groups(breadcrumb, r'トップ >(.*?)>(.*)')
                if g:
                    r['top_category'], r['sub_category'] = g
                
                return r

        """
        matches = re.search(regex, test_str, re.DOTALL | re.UNICODE)

        if matches:
            return matches.groups()


    @staticmethod
    def multireplace(string, replacements, ignore_case=False):
        """
        Given a string and a replacement map, it returns the replaced string.
        :param str string: string to execute replacements on
        :param dict replacements: replacement dictionary {value to find: value to replace}
        :param bool ignore_case: whether the match should be case insensitive
        :rtype: str
        @see https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
        """
        # If case insensitive, we need to normalize the old string so that later a replacement
        # can be found. For instance with {"HEY": "lol"} we should match and find a replacement for "hey",
        # "HEY", "hEy", etc.
        if ignore_case:
            def normalize_old(s):
                return s.lower()

            re_mode = re.IGNORECASE

        else:
            def normalize_old(s):
                return s

            re_mode = 0

        replacements = {normalize_old(key): val for key, val in replacements.items()}
        
        # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
        # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
        # 'hey ABC' and not 'hey ABc'
        rep_sorted = sorted(replacements, key=len, reverse=True)
        rep_escaped = map(re.escape, rep_sorted)
        
        # Create a big OR regex that matches any of the substrings to replace
        pattern = re.compile("|".join(rep_escaped), re_mode)
        
        # For each match, look up the new string in the replacements, being the key the normalized old string
        return pattern.sub(lambda match: replacements[normalize_old(match.group(0))], string)

class Html(object):
    """
    HTML辅助类
    """
    @staticmethod
    def remove_tags_attribute(text, which_ones=(), keep=(), encoding=None):
        """ Remove HTML Tags attribute only.

        `which_ones` and `keep` are both tuples, there are four cases:

        |``which_ones``  |  ``keep``      | what it does                                |
        |--------------  |:---------------|:------------------------------------------- |
        | **not empty**  |   empty        | remove all tags in ``which_ones``           |
        | empty          | **not empty**  | remove all tags except the ones in ``keep`` |
        | empty          | empty          | remove all tags                             |
        | **not empty**  |  **not empty** | not allowed                                 |
        """

        assert not (which_ones and keep), 'which_ones and keep can not be given at the same time'

        which_ones = {tag.lower() for tag in which_ones}
        keep = {tag.lower() for tag in keep}

        def will_remove(tag):
            tag = tag.lower()
            if which_ones:
                return tag in which_ones
            else:
                return tag not in keep

        def remove_tag(m):
            tag = m.group(1)
            return "<{}>".format(m.group(1)) if will_remove(tag) else m.group(0)

        regex = r"<([a-zA-Z!].*?)\s+.*?>"
        retags = re.compile(regex, re.DOTALL | re.IGNORECASE)
        return retags.sub(remove_tag, to_unicode(text, encoding))

    @staticmethod
    def is_valid_url(url, base_url=""):
        """
        判断url是否合法

        示例:

            print is_valid_url("abc:fddfd")
            print is_valid_url("/localhost")
            print is_valid_url("/localhost/test")
            print is_valid_url("http://localhost/test")
            print is_valid_url("//localhost/test", "http://localhost")
            print is_valid_url("/test", "http://localhost")

        输出结果:

            False
            False
            False
            True
            True
            True
        """
        result = urlparse(urljoin(base_url, url))
        if result.scheme and result.netloc:
            return True
        else:
            return False

    @staticmethod
    def clean_content(content, **kwargs):
        """
        @see lxml.html.Cleaner \n
            scripts = True
            javascript = True
            comments = True
            style = False
            inline_style = None
            links = True
            meta = True
            page_structure = True
            processing_instructions = True
            embedded = True
            frames = True
            forms = True
            annoying_tags = True
            remove_tags = None
            allow_tags = None
            kill_tags = None
            remove_unknown_tags = True
            safe_attrs_only = True
            safe_attrs = defs.safe_attrs
            add_nofollow = False
            host_whitelist = ()
            whitelist_tags = set(['iframe', 'embed'])
        """
        default_params = {
            "style" : True,
            "inline_style" : True,
            'remove_tags': ('font'),
            "safe_attrs" : ('data-src', 'data-type', 'src', 'href'),
            # 'whitelist_tags' : set(['embed']),
        }
        merged_params = dict(kwargs, **default_params)
        cleaner = clean.Cleaner(**merged_params)
        return cleaner.clean_html(content)

    @staticmethod
    def clean_html(content):
        try:
            doc = html.document_fromstring(content)
            text = doc.text_content()
            text = re.sub(r"[\t\n\r]", "", text)
        except:
            return ''
        return text