import tqdm
import json
import torch
import torchvision.transforms as tf
import torchvision.models as models
import torchvision.datasets as ds
import numpy as np
from PIL import Image

#initialize some variables
#-------------------------
c_tp = 0
gt = 0
att_succ = 0
att_fail = 0
recov = 0
lost = 0

#load the class dictionary
#------------------------
class_file = open("./imagenet_class_index.json")
class_idx = json.load(class_file)
idx2label = [class_idx[str(k)][1] for k in range(len(class_idx))]

#load the model
#VGG16 / VGG19 / ResNet18 / Resnet50 / Resnet101 / InceptionV3
#---------------
#pascal07 models
model = torch.load("D:/PHD_Bilel/classification_tests/vgg19_pas07.pth")
#model = torch.load('D:/PHD_Bilel/defense_codes/PatchCleanser-main/checkpoints/resnet50_imagenet_model.pth')


#pretrained imagenet
#model = models.inception_v3(pretrained = True)

model.cuda()
model.eval()

# load image from disk
#----------------------
# img = Image.open("D:/PHD_Bilel/casia adv tests/casia_1p/p18/001-nm-01-018-041.jpg")
# img = img.resize((224,224))
# timg = tf.ToTensor()(img)

# timg = torch.unsqueeze(timg, 0)

ls = 0
#load image from pytorch structure
#---------------------------------
clean_ds = ds.ImageFolder(root = "D:/PHD_Bilel/Datasets/autoenc/pascal_07/clean/",
                   )
patch_ds = ds.ImageFolder(root = "D:/PHD_Bilel/Datasets/patch_shape_tests/pascal_07/patch_advpatch_combi/",
                   )
inpaint_ds = ds.ImageFolder(root = "D:/PHD_Bilel/Datasets/autoenc/pascal_07/clean/",
                   )
for f in tqdm.tqdm(range(len(clean_ds)), position=0, leave=True):
    c_img , c_tgt = clean_ds.__getitem__(f)
    c_img = c_img.resize((224,224))
    c_timg = tf.ToTensor()(c_img).cuda()
    
    
    p_img , p_tgt =patch_ds.__getitem__(f)
    p_img = p_img.resize((224,224))
    p_timg = tf.ToTensor()(p_img).cuda()
    
    
    i_img , i_tgt = inpaint_ds.__getitem__(f)
    i_img = i_img.resize((224,224))
    i_timg = tf.ToTensor()(i_img).cuda()
    
    
    #normalize the image prior to classification
    #docs say this is needed
    #-------------------------------------------------
    normalize = tf.Normalize(mean=[0.485, 0.456, 0.406],
                                      std=[0.229, 0.224, 0.225])
    
    c_timg = normalize(c_timg)
    c_timg.cuda()
    
    p_timg = normalize(p_timg)
    p_timg.cuda()
    
    i_timg = normalize(i_timg)
    i_timg.cuda()
    
    c_timg = torch.unsqueeze(c_timg, 0)
    p_timg = torch.unsqueeze(p_timg, 0)
    i_timg = torch.unsqueeze(i_timg, 0)
    
    #Run the classification
    #----------------------
    c_out = model(c_timg)
    p_out = model(p_timg)
    i_out = model(i_timg)
    
    #display predicted class and stats
    #---------------------------------
    gt = gt + 1
    c_pred = int(c_out[0].argmax(0))
    p_pred = int(p_out[0].argmax(0))
    i_pred = int(i_out[0].argmax(0))
    
    

    
    if c_pred == c_tgt:
        c_tp = c_tp + 1
        if p_pred != c_pred:
            att_succ = att_succ + 1
            if i_pred == c_pred:
                recov = recov + 1
        else:
            att_fail = att_fail + 1
            if i_pred != c_pred:
                lost = lost + 1
            
    
    
        
    correct_pred_pct = round((c_tp/gt) * 10000) / 100
    if c_tp > 0:
        att_succ_pct = round((att_succ/c_tp) * 10000) / 100
    if att_succ > 0:
        recov_pct = round((recov/att_succ) * 10000) / 100
    if lost > 0:
        lost_pct = round((lost/att_fail) * 10000) / 100
    
    #print("Predicted: " + idx2label[pred] + " Actual: " + idx2label[tgt])
    #print("Detection accuracy :" + str(tp) + "/" + str(gt) + " (" + str(ratio) + ")")
print()
print("Detection accuracy :" + str(c_tp) + "/" + str(gt) + " (" + str(correct_pred_pct) + ")")
print("Adversarial attack success :" + str(att_succ) + "/" + str(c_tp) + " (" + str(att_succ_pct) + ")")
print("Recovered predictions :" + str(recov) + "/" + str(att_succ) + " (" + str(recov_pct) + ")")
print("Lost correct predictions :" + str(lost) + "/" + str(att_fail) + " (" + str(lost_pct) + ")")
torch.cuda.empty_cache()