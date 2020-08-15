#!/usr/bin/env bash
CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 python -u robust_parser.py --mode train --config configs/parsing/robust.json \
 --num_epochs 400 --patient_epochs 100 --batch_size 32 --eval_batch_size 64 --seed 0 \
 --opt adamw --schedule exponential --learning_rate 0.002 --lr_decay 0.75 --decay_steps 5000 \
 --beta1 0.9 --beta2 0.98 --eps 1e-12 --grad_clip 5.0 --weight_decay 1e-5 \
 --loss_type token --warmup_steps 0 --reset 0 --eval_every 1 --unk_replace 1.0 \
 --word_embedding sskip --word_path "data/en.small-100.bin.gz" --char_embedding random \
 --pretrained_lm none --lm_path "/mnt/hgfs/share/xlm-roberta-base" --noscreen \
 --punctuation '.' '``' "''" ':' ',' \
 --format conllx \
 --train "data/ptb_two_auto.conll" \
 --dev "data/ptb_two_auto.conll" \
 --test "data/ptb_two_auto.conll" \
 --model_path "models/parsing/robust" \
 --normalize_digits
 #--mix_datasets \
 #--punctuation 'PUNCT' --pos_idx 3 \
 #--freeze --basic_word_embedding 
