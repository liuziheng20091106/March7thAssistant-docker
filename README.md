# March7thAssistant for Docker

## 如何使用

1. [安装Docker](https://yeasy.gitbook.io/docker_practice/install)和 `Docker Compose`
2. 按照[PaddleOCR-json V1.4 Docker 部署指南](https://github.com/hiroi-sora/PaddleOCR-json/blob/main/cpp/README-docker.md)进行部署
3. 将你的配置文件与账号信息（`config.yaml`与`settings\*.enc`）复制到对于目录下
4. clone 本仓库，接着我们使用Docker Compose部署项目：`docker-compose up -d`


> [!NOTE]
> PaddleOCR-json的镜像名必须为`paddleocr-json`,默认的`docker build -t paddleocr-json .`即可满足此要求。
> 
> 若非要更改镜像名，请手动修改`docker-compose.yaml`

> [!TIP]
> 如果PaddleOCR-json镜像编译过慢，我们也可以考虑手动修改镜像源来进行加速，比如在Dockerfile中添加以下命令
> 
> `RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources`
> 
> 或者从本项目的发行版里下载预编译好的镜像进行导入

> [!NOTE]
> 请常查询日志以了解运行状态
> 将运行后设置为`循环(loop)`以持久运行容器

> [!TIP]
> 修改配置文件后无需重启容器，在下次启动时会重载配置文件

## 系统要求
- CPU：两核以上
- Mem：1.5G以上
- GPU：无
- 磁盘：能用就行

## 更新
本项目由于对原版March7thAssistant修改过多，无法正常与其同步，后续可能会考虑解决此问题。在此之前，项目会不定期与March7thAssistant进行同步

未发生大改动时，在项目文件夹下执行`git pull`即可更新。更新后请重启容器

## 项目关联
March7thAssistant for Docker 离不开以下开源项目的帮助：

- 源项目[https://github.com/moesnow/March7thAssistant](https://github.com/moesnow/March7thAssistant)
- OCR文字识别 [https://github.com/hiroi-sora/PaddleOCR-json](https://github.com/hiroi-sora/PaddleOCR-json)
