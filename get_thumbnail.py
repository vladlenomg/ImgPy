from PIL import Image

def get_thumbnail(imgpath, save_name):
	img = Image.open(imgpath)
	size = (400, 350)
	img_ratio = img.size[0] / float(img.size[1])
	ratio = size[0] / float(size[1])

	if img.format == 'GIF': 
		print("gif!")
		img = img.convert('RGB')

	if ratio > img_ratio:
		img = img.resize((size[0], int(round(size[0] * img.size[1] / img.size[0]))),Image.ANTIALIAS)
		box = (0, int(round((img.size[1] - size[1]) / 2)), img.size[0],int(round((img.size[1] + size[1]) / 2)))
		img = img.crop(box)
	elif ratio < img_ratio:
		img = img.resize((int(round(size[1] * img.size[0] / img.size[1])), size[1]),Image.ANTIALIAS)
		box = (int(round((img.size[0] - size[0]) / 2)), 0,int(round((img.size[0] + size[0]) / 2)), img.size[1])
		img = img.crop(box)
	else :
	        img = img.resize((size[0], size[1]), Image.ANTIALIAS)

	img.save(save_name, "JPEG")