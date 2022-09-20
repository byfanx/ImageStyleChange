import os

from django.http import StreamingHttpResponse
from django.shortcuts import render,HttpResponse
import random
import numpy as np
import cv2
import uuid
import json
from PIL import Image as  PILImage
from PIL import ImageDraw
from PIL import ImageFont
import time


from ImageStyleChange import settings
from imgsApp.models import Image

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = str(settings.BASE_DIR)
IMGS_DIR = os.path.join(os.path.join(BASE_DIR, 'static'), 'images\\')
IMGS_URL = settings.STATIC_URL+"images/"
# Create your views here.

"""
    上传图片
"""
def upload(req):
    if req.method == 'POST':
        user_id = req.POST.get('userId')
        # print("user_id="+user_id)
        file = req.FILES.get('file')
        # print("fileName===="+file.name)
        # 上传的文件名
        imgInput_FileName = file.name
        width = req.POST.get('width')
        height = req.POST.get('height')

        '''创建uuid作为文件名，创建一个查看当前uuid是否被占用，如果已经占用，那么就重新生成'''
        # while True:
        #     uuid_str = uuid.uuid4().hex
        #     imgInput_FileName = uuid_str+".jpg"
        #     imglist = Image.objects.filter(img_url=imgInput_FileName)
        #     if not imglist.exists():
        #         break


        # 保存到服务器的文件名
        imgOutput_FileName = imgInput_FileName

        # print("BASE_DIR="+BASE_DIR)
        # print("BASE_SET_DIR=",BASE_DIR)
        # print("BASE_SET_DIR="+str(type(BASE_SET_DIR)))
        # print("IMGS_DIR="+str(IMGS_DIR))
        # print("IMGS_URL=",IMGS_URL)

        # 将图片写入本地持久化存储
        destination = open(os.path.join(IMGS_DIR,imgOutput_FileName),'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        # 数据库中不存在该数据，才会存储
        if not imglist.exists():
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=user_id, img_url=imgOutput_FileName,width=width,height=height)

        data = {
            'status':200,
            'massage':"上传成功",
            'data':{
                'fileUrl':IMGS_URL,
                'fileName':imgOutput_FileName
            }
        }
        # return render(req,'main.html',data)
        return HttpResponse(json.dumps(data))

"""
    下载图片
"""
def download(req):
    if req.method == 'POST':
        id = req.POST.get('id')
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=",imgInput_FileName)
        response = StreamingHttpResponse(open(IMGS_DIR + imgInput_FileName,'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = "attachment; filename="+imgInput_FileName
        return response

"""
    原图
"""
def original(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=",imgInput_FileName)


        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgInput_FileName
            }
        }
        return HttpResponse(json.dumps(data))

"""
    转换成素描
    https://blog.csdn.net/weixin_39760433/article/details/111161134?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522162210242116780269864693%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=162210242116780269864693&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_v2~rank_v29-5-111161134.first_rank_v2_pc_rank_v29&utm_term=opencv%E5%9B%BE%E5%83%8F%E9%A3%8E%E6%A0%BC%E8%BD%AC%E5%8C%96%E6%84%8F%E4%B9%89&spm=1018.2226.3001.4187
"""
def sketch(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=",imgInput_FileName)
        # 转换过后的文件名为：原文件名-sketch.原文件格式
        imgOutput_FileName = imgInput_FileName[:-4] + "-sketch" + imgInput_FileName[-4:]

        print(imgOutput_FileName)
        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            a = np.asarray(PILImage.open(IMGS_DIR + imgInput_FileName).convert('L')).astype('float')  # 转化为灰度图
            depth = 10.  # (0-100) 可以理解为图像的深淡程度
            grad = np.gradient(a)  # 取图像灰度的梯度值
            grad_x, grad_y = grad  # 分别取横纵图像梯度值
            grad_x = grad_x * depth / 100.
            grad_y = grad_y * depth / 100.
            A = np.sqrt(grad_x ** 2 + grad_y ** 2 + 1.)  # 构造x和y轴梯度的三维归一化单位坐标系
            uni_x = grad_x / A
            uni_y = grad_y / A
            uni_z = 1. / A
            vec_el = np.pi / 2.2  # 光源的俯视角度，弧度值
            vec_az = np.pi / 4.  # 光源的方位角度，弧度值
            dx = np.cos(vec_el) * np.cos(vec_az)  # 光源对x 轴的影响
            dy = np.cos(vec_el) * np.sin(vec_az)  # 光源对y 轴的影响
            dz = np.sin(vec_el)  # 光源对z 轴的影响
            b = 255 * (dx * uni_x + dy * uni_y + dz * uni_z)  # 光源归一化 梯度与光源相互作用，将梯度转化为灰度
            b = b.clip(0, 255)  # 为避免数据越界，将生成的灰度值裁剪至0‐255区间
            im = PILImage.fromarray(b.astype('uint8'))  # 重构图像
            im.save(IMGS_DIR + imgOutput_FileName)

            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId,img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }
        return HttpResponse(json.dumps(data))


"""
    转换成线稿
    https://blog.csdn.net/weixin_39059031/article/details/82724951
"""
def LineDraft(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=",imgInput_FileName)
        # 转换过后的文件名为：原文件名-sketch.原文件格式
        imgOutput_FileName = imgInput_FileName[:-4] + "-LineDraft" + imgInput_FileName[-4:]

        print(imgOutput_FileName)
        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            img_gray = cv2.imread(IMGS_DIR + imgInput_FileName, 0)
            img_blur = cv2.GaussianBlur(img_gray, (21, 21), 0, 0)
            img_blend = cv2.divide(img_gray, img_blur, scale=256)
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, img_blend)

            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId,img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }
        return HttpResponse(json.dumps(data))

"""
    转换成卡通
    http://www.zzvips.com/article/128976.html
"""
def cartoon(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-cartoon" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            num_down = 2  # 缩减像素采样的数目
            num_bilateral = 7  # 定义双边滤波的数目
            img_rgb = cv2.imread(IMGS_DIR + imgInput_FileName)  # 读取图片
            # 用高斯金字塔降低取样
            img_color = img_rgb
            # for _ in range(num_down):
            #     img_color = cv2.pyrDown(img_color)
            # 重复使用小的双边滤波代替一个大的滤波[图片]
            for _ in range(num_bilateral):
                img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)
            # 升采样图片到原始大小
            #     for _ in range(num_down):
            #         img_color = cv2.pyrUp(img_color)
            # 转换为灰度并且使其产生中等的模糊
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            img_blur = cv2.medianBlur(img_gray, 7)
            # 检测到边缘并且增强其效果
            img_edge = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=9, C=2)
            # 转换回彩色图像
            img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
            img_cartoon = cv2.bitwise_and(img_color, img_edge)
            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, img_cartoon)

            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)

        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))

"""
    转换成灰度
"""
def gray(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-gray" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            img = cv2.imread(IMGS_DIR + imgInput_FileName)
            gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, gray_img)
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)

        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))


"""
    围绕x轴，垂直翻转
"""
def xFlip(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-xFlip" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            img = cv2.imread(IMGS_DIR + imgInput_FileName)
            xFlip_img = cv2.flip(img,0)
            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, xFlip_img)
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))

"""
    围绕y轴，水平翻转
"""
def yFlip(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-yFlip" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            img = cv2.imread(IMGS_DIR + imgInput_FileName)

            xFlip_img = cv2.flip(img,1)
            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, xFlip_img)
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))

"""
    围绕中心，对角翻转
"""
def centre(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-centre" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            img = cv2.imread(IMGS_DIR + imgInput_FileName)
            xFlip_img = cv2.flip(img,-1)
            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, xFlip_img)
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))

"""
    转换成字符画
    https://zhuanlan.zhihu.com/p/56033037
"""
def strimg(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-strimg" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            """
                利用 聚类 将像素信息聚为3或5类，颜色最深的一类用数字密集地表示，阴影的一类用“-”横杠表示，明亮部分空白表示。
                ---------------------------------
                frame：需要传入的图片信息。可以是opencv的cv2.imread()得到的数组，也可以是Pillow的Image.read()。
                K：聚类数量，推荐的K为3或5。根据经验，3或5时可以较为优秀地处理很多图像了。若默认的K=5无法很好地表现原图，请修改为3进行尝试。若依然无法很好地表现原图，请换图尝试。 （ -_-|| ）
                ---------------------------------
                聚类数目理论可以取大于等于3的任意整数。但水平有限，无法自动判断当生成的字符画可以更好地表现原图细节时，“黑暗”、“阴影”、”明亮“之间边界在哪。所以说由于无法有效利用更大的聚类数量，那么便先简单地限制聚类数目为3和5。
                """
            K = 3
            strImg = cv2.imread(IMGS_DIR + imgInput_FileName)

            if type(strImg) != np.ndarray:
                strImg = np.array(strImg)

            height, width, *_ = strImg.shape  # 有时返回两个值，有时三个值
            frame_gray = cv2.cvtColor(strImg, cv2.COLOR_BGR2GRAY)
            frame_array = np.float32(frame_gray.reshape(-1))

            # 设置相关参数。
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            flags = cv2.KMEANS_RANDOM_CENTERS
            # 得到labels(类别)、centroids(矩心)。
            # 如第一行6个像素labels=[0,2,2,1,2,0],则意味着6个像素分别对应着 第1个矩心、第3个矩心、第3、2、3、1个矩心。
            compactness, labels, centroids = cv2.kmeans(frame_array, K, None, criteria, 10, flags)
            centroids = np.uint8(centroids)

            # labels的数个矩心以随机顺序排列，所以需要简单处理矩心.
            centroids = centroids.flatten()
            centroids_sorted = sorted(centroids)
            # 获得不同centroids的明暗程度，0最暗
            centroids_index = np.array([centroids_sorted.index(value) for value in centroids])

            bright = [abs((3 * i - 2 * K) / (3 * K)) for i in range(1, 1 + K)]
            bright_bound = bright.index(np.min(bright))
            shadow = [abs((3 * i - K) / (3 * K)) for i in range(1, 1 + K)]
            shadow_bound = shadow.index(np.min(shadow))

            labels = labels.flatten()
            # 将labels转变为实际的明暗程度列表，0最暗。
            labels = centroids_index[labels]
            # 列表解析，每2*2个像素挑选出一个，组成（height*width*灰）数组。
            labels_picked = [labels[rows * width:(rows + 1) * width:2] for rows in range(0, height, 2)]

            scale = 3
            canvas = np.zeros((scale * height, scale * width, 3), np.uint8)
            canvas.fill(255)  # 创建长宽为原图的白色画布。

            # 因为 字体大小为0.45时，每个数字占6*6个像素，而白底画布为原图
            # 所以 需要原图中每2*2个像素中挑取一个，在白底画布中由6*6像素大小的数字表示这个像素信息。
            y = 0
            for rows in labels_picked:
                x = 0
                for cols in rows:
                    if cols <= shadow_bound:
                        cv2.putText(canvas, str(random.randint(2, 9)),
                                    (x, y), cv2.FONT_HERSHEY_PLAIN, 0.45, 1)
                    elif cols <= bright_bound:
                        cv2.putText(canvas, "-", (x, y),
                                    cv2.FONT_HERSHEY_PLAIN, 0.4, 0, 1)
                    x += (2*scale)
                y += (2*scale)


            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, canvas)
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))

"""
    转换成彩色字符画
    https://blog.csdn.net/u012424313/article/details/105225562/
"""
def strimgColor(req):
    userId = req.POST.get("user_id")
    imgInput_FileName = req.POST.get('fileName')
    strIn = req.POST.get('str')
    if len(strIn)<=0 or strIn==None:
        strIn="ABCDE"
    print("imgInput_FileName=" + imgInput_FileName)
    imgOutput_FileName = imgInput_FileName[:-4] + "-strimgColor-" + strIn + imgInput_FileName[-4:]

    imglist = Image.objects.filter(img_url=imgOutput_FileName)
    if not imglist.exists():
        # 读取图片信息
        print("IMGS_DIR + imgInput_FileName=="+IMGS_DIR + imgInput_FileName)
        old_img = PILImage.open(IMGS_DIR + imgInput_FileName)
        pix = old_img.load()
        width = old_img.size[0]
        height = old_img.size[1]

        # 创建新图片
        scale = 3           # 放大的倍数，因为字符大小的原因，不放大字符会堆积在一个很小的像素点，导致看不到字符
        sample_step = 3
        canvas = np.ndarray((height * scale, width * scale, 3), np.uint8)
        canvas[:, :, :] = 255
        new_image = PILImage.fromarray(canvas)
        draw = ImageDraw.Draw(new_image)

        # font = ImageFont.truetype("consola.ttf", 10)
        font = ImageFont.truetype('simsun.ttc', 10)
        char_table = list(strIn)

        # 开始绘制
        pix_count = 0
        table_len = len(char_table)
        for y in range(height):
            for x in range(width):
                if x % sample_step == 0 and y % sample_step == 0:
                    draw.text((x * scale, y * scale), char_table[pix_count % table_len], pix[x, y], font)
                    pix_count += 1

        # 保存转换后的图片
        new_image.save(IMGS_DIR + imgOutput_FileName)
        # 图片信息保存到数据库
        image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
    data = {
        'status': 200,
        'massage': "转换成功",
        'data': {
            'fileUrl': IMGS_URL,
            'fileName': imgOutput_FileName
        }
    }

    return HttpResponse(json.dumps(data))


"""
    转成浮雕效果
    https://zhuanlan.zhihu.com/p/51183305
"""
def emboss(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-emboss" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            img = cv2.imread(IMGS_DIR + imgInput_FileName)

            imgInfo = img.shape
            height = imgInfo[0]
            width = imgInfo[1]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            dstImg = np.zeros((height, width, 1), np.uint8)
            # 算法：newPixel = grayCurrentPixel - grayNextPixel + 150
            for i in range(0, height):
                for j in range(0, width - 1):
                    grayCurrentPixel = int(gray[i, j])
                    grayNextPixel = int(gray[i, j + 1])
                    newPixel = grayCurrentPixel - grayNextPixel + 150
                    if newPixel > 255:
                        newPixel = 255
                    if newPixel < 0:
                        newPixel = 0
                    dstImg[i, j] = newPixel
            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, dstImg)
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))


"""
    转换成负片
"""
def dipian(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-dipian" + imgInput_FileName[-4:]

        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            img = cv2.imread(IMGS_DIR + imgInput_FileName)

            dist = 255 - img
            # 保存转换后的图片
            cv2.imwrite(IMGS_DIR + imgOutput_FileName, dist)
            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName
            }
        }

        return HttpResponse(json.dumps(data))


"""
    风格迁移
    https://zhuanlan.zhihu.com/p/50852257
"""
def transfer(req):
    if req.method == 'POST':
        userId = req.POST.get("user_id")
        imgInput_FileName = req.POST.get('fileName')
        style = req.POST.get('style')
        modelsImg = style+".jpg"
        model = "G:\\CodeSpace\\ImageStyleChange\\static\\models\\instance_norm\\"+style+".t7"
        # 0 - 100，设置输出图片的质量，默认80，越大图片质量越好
        jpg_quality = 80
        # 设置风格化图片的宽度，默认为None, 即原始图片尺寸
        width = None
        print("imgInput_FileName=" + imgInput_FileName)
        imgOutput_FileName = imgInput_FileName[:-4] + "-" + style + imgInput_FileName[-4:]
        print("imgOutput_FileName=" + imgOutput_FileName)
        imglist = Image.objects.filter(img_url=imgOutput_FileName)
        if not imglist.exists():
            ## 读入原始图片，调整图片至所需尺寸，然后获取图片的宽度和高度
            img = cv2.imread(IMGS_DIR + imgInput_FileName)
            (h, w) = img.shape[:2]
            if width is not None:
                img = cv2.resize(img, (width, round(width*h/w)), interpolation=cv2.INTER_CUBIC)
                (h, w) = img.shape[:2]

            ## 从本地加载预训练模型
            print('加载预训练模型......')
            net = cv2.dnn.readNetFromTorch(model)

            ## 将图片构建成一个blob：设置图片尺寸，将各通道像素值减去平均值（比如ImageNet所有训练样本各通道统计平均值）
            ## 然后执行一次前馈网络计算，并输出计算所需的时间
            blob = cv2.dnn.blobFromImage(img, 1.0, (w, h), (103.939, 116.779, 123.680), swapRB=False, crop=False)
            net.setInput(blob)
            start = time.time()
            output = net.forward()
            end = time.time()
            print("风格迁移花费：{:.2f}秒".format(end - start))

            ## reshape输出结果, 将减去的平均值加回来，并交换各颜色通道
            output = output.reshape((3, output.shape[2], output.shape[3]))
            output[0] += 103.939
            output[1] += 116.779
            output[2] += 123.680
            output = output.transpose(1, 2, 0)

            ## 输出风格化后的图片
            cv2.imwrite(IMGS_DIR+imgOutput_FileName, output, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])

            # 图片信息保存到数据库
            image = Image.objects.create(user_id=userId, img_url=imgOutput_FileName)
        data = {
            'status': 200,
            'massage': "转换成功",
            'data': {
                'fileUrl': IMGS_URL,
                'fileName': imgOutput_FileName,
                'modelsImg': "/static/models/style_images/"+modelsImg
            }
        }

        return HttpResponse(json.dumps(data))