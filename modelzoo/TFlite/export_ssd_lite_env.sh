INPUT_TYPE=image_tensor

MODEL=ssd_mobilenet_v1_coco_2018_01_28
ROOT=${HOME}/models/${MODEL}

PIPELINE_CONFIG_PATH=${ROOT}/pipeline.config
TRAINED_CKPT_PREFIX=${ROOT}/model.ckpt
EXPORT_DIR=${HOME}/exported/${MODEL}

python object_detection/export_tflite_ssd_graph.py \
    --pipeline_config_path=${PIPELINE_CONFIG_PATH} \
    --trained_checkpoint_prefix=${TRAINED_CKPT_PREFIX} \
    --output_directory=${EXPORT_DIR} \
    --add_postprocessing_op=true