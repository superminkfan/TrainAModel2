import os, torch, wandb

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import (
    LoraConfig,
    PeftModel,
    prepare_model_for_kbit_training,
    get_peft_model,
)

from datasets import load_dataset
from trl import SFTTrainer, setup_chat_format
from dataclasses import dataclass

# Настройка Weights & Bias для логирования при обучении

from huggingface_hub import login
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()

hf_token = user_secrets.get_secret("huggingface_token")

login(token = hf_token)

wb_token = user_secrets.get_secret("wandb_api_key")

wandb.login(key=wb_token)
run = wandb.init(
    project='Fine-tune Llama 3.1 8B on Medical Dataset',
    job_type="training",
    anonymous="allow"
)

def trainAModel():
    print("start training!")


if __name__ == '__main__':
    trainAModel()


