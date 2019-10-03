FROM continuumio/miniconda3

WORKDIR /home/svision

COPY yolov3/ ./
COPY configs.json ./
COPY environment.yml ./
COPY service_detect.py ./
COPY start_svision.sh ./

RUN chmod +x start_svision.sh
RUN conda env create -f environment.yml
RUN echo "source activate svision" > ~/.bashrc

ENV PATH /opt/conda/envs/svision/bin:$PATH

EXPOSE 50001

ENTRYPOINT ["./start_svision.sh"]
