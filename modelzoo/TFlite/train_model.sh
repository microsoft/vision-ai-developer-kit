$CONFIG_FILE={path to the config file for the pipeline}
$CHECKPOINT_OUTPUT_DIR={path to write checkpoint files to}

python model_main.py \
	--model_dir=$CHECKPOINT_OUTPUT_DIR \
	--pipeline_config_path=$CONFIG_FILE \
	--num_train_steps=50000 \ 
	--num_eval_steps=500 \
	--logtostderr