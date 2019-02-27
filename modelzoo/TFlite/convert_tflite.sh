MODEL=ssd_mobilenet_v1_coco_2018_01_28
ROOT=${HOME}/exported/${MODEL}

INPUT=normalized_input_image_tensor
OUTPUT=TFLite_Detection_PostProcess,TFLite_Detection_PostProcess:1,TFLite_Detection_PostProcess:2,TFLite_Detection_PostProcess:3

OUT_FILE=${ROOT}/ssd_graph.tflite
IN_FILE=${ROOT}/tflite_graph.pb

${HOME}/git/tensorflow/bazel-bin/tensorflow/contrib/lite/python/tflite_convert \
    --output_file=${OUT_FILE} \
    --graph_def_file=${IN_FILE} \
    --input_arrays=${INPUT} \
    --input_shapes=1,300,300,3 \
    --output_arrays=${OUTPUT} \
    --inference_type=FLOAT \
    --dump_graphviz_dir=${ROOT} \
    --allow_custom_ops
