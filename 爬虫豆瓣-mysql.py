#-*- codeing = utf-8 -*-
from bs4 import BeautifulSoup  #网页分析，获取数据
import re   #正则表达式
import xlwt   #excel表格
import urllib.request,urllib.error   #指定URL，获取网页数据
import pymysql   #进行MySQL数据操作

'''
1.爬取网页
2.解析数据
3.保存数据
'''

def main():
    baseurl = 'https://movie.douban.com/top250?start='
    datalist=getData(baseurl)
    #savepath=r'.\豆瓣电影TOP250.xls'
    #saveData(datalist,savepath)
    saveMysql(datalist)


findLink = re.compile(r'<a href="(.*?)">')    #compile创建正则表达式
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)
findTitle = re.compile(r'<span class="title">(.*)</span>')
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findJudge = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'<span class="inq">(.*)</span>')
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

#爬取网页
def getData(baseurl):
    datalist=[]
    for i in range(0,10):
        url = baseurl + str(i*25)
        html = askUrl(url)
        soup = BeautifulSoup(html,'html.parser')
        for item in soup.find_all('div',class_="item"):
            #print(item)  #测试查看电影所有item信息
            data = []
            item = str(item)
            link = re.findall(findLink,item)[0]
            data.append(link)
            imgsrc = re.findall(findImgSrc,item)[0]
            data.append(imgsrc)
            titles = re.findall(findTitle,item)
            if (len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace('/','')
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append(' ')
            rating = re.findall(findRating,item)[0]
            data.append(rating)
            judge = re.findall(findJudge,item)[0]
            data.append(judge)
            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq = inq[0].replace('。','')
                data.append(inq)
            else:
                data.append(' ')
            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?',' ',bd)
            bd = re.sub('/',' ',bd)
            data.append(bd.strip())    #strip去掉前后空格
            # print(data)
            datalist.append(data)

    return datalist


def askUrl(url):
    head={
        'User-Agent': 'Mozilla / 5.0(Windows NT 6.1;Win64;x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 100.0.4896.75 Safari / 537.36'
    }
    request=urllib.request.Request(url,headers=head)
    html=''
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,'code'):
            print(e,'code')
        if hasattr(e,'reason'):
            print(e,'reason')
    return html
#保存数据到excel
def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet = book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True)
    col = ('电影详情连接','图片连接','影片中文名','影片外国名','评分','评价数','概况','相关信息')
    for i in range(0,8):
        sheet.write(0,i,col[i])  #列名
    for i in range(0,250):
        print('第%d条'%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])
    book.save(savepath)


#数据库保存
def saveMysql(datalist):
    #连接数据库
    db = pymysql.connect(host='localhost',user='root',password='root',port=3306,charset='utf8')
    #创建游标对象
    cursor = db.cursor()
    #执行语句
    cursor.execute('use text;')
    try:
        sql = '''create table if not exists top250 (
              id int primary key auto_increment,
              m_url varchar(400) not null,
              p_url varchar(400) not null,
              name1 varchar(400),
              name2 varchar(400),
              mark float not null,
              people int not null,
              general varchar(400) not null,
              information varchar(400) not null);
        '''
        cursor.execute(sql)
    except pymysql.Error as e:
        print('创建失败！'+e)

    for data in datalist:
        for index in range(len(data)):
            data[index] = '"'+data[index]+'"'
        sql1 = '''
        insert into top250(m_url,p_url,name1,name2,mark,people,general,information) 
        values(%s);'''%','.join(data)
        #print(sql1)
        try:
            cursor.execute(sql1)

        except pymysql.Error as e:
            print('储存数据失败！'+e)
    cursor.execute('select * from top250;')
    data = cursor.fetchall()    #接收返回结果
    db.commit()
    print(data)
    db.close()

if __name__=='__main__':
    main()
    #saveMysql()
    #print('爬取完毕！')