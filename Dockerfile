FROM python:3.11-alpine

LABEL maintainer="Dave Cook <dave@binx.ca>"
LABEL description="Healthcare VOC Compliance Calculator — Python engine with datasets"
LABEL org.opencontainers.image.source="https://github.com/DaveCookVectorLabs/healthcare-voc-compliance"
LABEL org.opencontainers.image.documentation="https://www.binx.ca/guides/healthcare-voc-compliance-guide.pdf"
LABEL org.opencontainers.image.vendor="Binx Professional Cleaning — https://www.binx.ca/commercial.php"

WORKDIR /app

# Install Python dependencies
COPY engines/python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy engine and datasets
COPY engines/python/engine.py .
COPY datasets/voc_regulatory_limits.csv datasets/
COPY datasets/healthcare_cleaning_products_voc.csv datasets/

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:8001/health || exit 1

CMD ["python", "engine.py", "--serve", "--port", "8001"]
