import torch.nn as nn
import math
import torch.nn.functional as F

class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes,stride=1):
        "ECA是指bb2是否加ECA，bb1是本身就不加的"
        super(BasicBlock, self).__init__()
        # bb1
        self.bb1 = nn.Sequential(nn.Conv2d(inplanes, planes, kernel_size=3, stride=stride,padding=1, bias=False),
                                 nn.BatchNorm2d(planes))

        # bb2=bb2+ECA
        bb2 = [nn.Conv2d(planes, planes, kernel_size=3, stride=1,padding=1, bias=False),
               nn.BatchNorm2d(planes)]

        # TODO：新增block添加进bb2中

        self.bb2 = nn.Sequential(*bb2)

        # 旁支下采样
        self.downsample = nn.Sequential()
        if stride != 1 or inplanes != planes:
            self.downsample = nn.Sequential(
                nn.Conv2d(inplanes, self.expansion * planes,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion * planes)
            )


    def forward(self, x):
        # x--->-------bb1------bb2------->
        #     ⬇                       ⬆
        #     ---(self.downsample)----
        residual = x

        x = F.relu(self.bb1(x))

        x = self.bb2(x)

        if self.downsample is not None:
            residual = self.downsample(residual)

        x += residual
        x = F.relu(x)

        return x


class unresnet_noInit(nn.Module):

    def __init__(self, num_classes=7):
        super(unresnet_noInit, self).__init__()

        self.head = nn.Sequential(nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1, bias=False),
                                  nn.BatchNorm2d(64))

        #__init__(self, inplanes, planes, ECA=False, stride=1, downsample=None, k_size=3):
        self.layer1 = nn.Sequential(BasicBlock(inplanes=64,  planes=64,  stride=1), BasicBlock(inplanes=64,  planes=64,  stride=1))
        self.layer2 = nn.Sequential(BasicBlock(inplanes=64,  planes=128, stride=2), BasicBlock(inplanes=128, planes=128, stride=1))
        self.layer3 = nn.Sequential(BasicBlock(inplanes=128, planes=256, stride=2), BasicBlock(inplanes=256, planes=256, stride=1))
        self.layer4 = nn.Sequential(BasicBlock(inplanes=256, planes=512, stride=2), BasicBlock(inplanes=512, planes=512, stride=1))

        self.avgpool = nn.AvgPool2d(4, stride=1)
        self.fc = nn.Linear(512, num_classes)
        #
        # for m in self.modules():
        #     if isinstance(m, nn.Conv2d):
        #         n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
        #         m.weight.data.normal_(0, math.sqrt(2. / n))
        #     elif isinstance(m, nn.BatchNorm2d):
        #         m.weight.data.fill_(1)
        #         m.bias.data.zero_()

    def forward(self, x):
        x = F.relu(self.head(x))    # 64*40*40

        x = self.layer1(x)  #64*40*40
        x = self.layer2(x)  # 128*20*20
        x = self.layer3(x)  # 256*10*10
        x = self.layer4(x)  # 512*5*5

        # x = self.avgpool(x)
        x = F.avg_pool2d(x, 4)  # [2, 512, 1, 1]
        x = x.view(x.size(0), -1)   # torch.Size([2, 512])
        x = self.fc(x)

        return x


if __name__ == "__main__":
    from torchsummary import summary

    model = unresnet_noInit().cuda()
    summary(model, input_size=(1, 40, 40))
    print(1)

    # == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
    # Total
    # params: 11, 171, 271
    # Trainable
    # params: 11, 171, 271
    # Non - trainable
    # params: 0
    # ----------------------------------------------------------------
    # Input
    # size(MB): 0.01
    # Forward / backward
    # pass
    # size(MB): 17.58
    # Params
    # size(MB): 42.62
    # Estimated
    # Total
    # Size(MB): 60.20
    # ----------------------------------------------------------------
