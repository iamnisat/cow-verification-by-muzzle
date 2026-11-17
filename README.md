## Model path
- Similarity model: `models/best_group_resnet50_model.pth`
- Detection model: `models/muzzle_detector_model.pt`

## Resourse
- Similarity model: https://drive.google.com/file/d/1Wnoqx0W2PRu6GEUfVweJE8aSiwPvvrlu/view?usp=sharing
- Detection model: https://drive.google.com/file/d/1eF0splXMrwZEHyJb33MftaaG6CqSmiBd/view?usp=sharing

## ------------ Google Cloud Platform ------------

# Google Cloud authentication

gcloud auth login

gcloud config set project upheld-setting-423215-p7

## Docker Image push to GCloud Artifact Registry

**Dockerfile Setup:** The Dockerfile uses a Python virtual environment to avoid root `pip` warnings and uses shell form for the CMD to properly handle Cloud Run's PORT environment variable.

gcloud builds submit \
  --tag us-central1-docker.pkg.dev/upheld-setting-423215-p7/development/cow-verification-by-muzzle

## Artifact Registry run deploy

gcloud run deploy cow-verification-by-muzzle \
--image=us-central1-docker.pkg.dev/upheld-setting-423215-p7/development/cow-verification-by-muzzle \
--port=8080 \
--region=us-central1 \
--allow-unauthenticated \
--platform managed
