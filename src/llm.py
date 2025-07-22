from llama_index.llms.bedrock_converse import BedrockConverse
import botocore.session

import os
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

def get_bedrock_llm():
    botocore_session = botocore.session.get_session()
    full_arn = 'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0'
    MODEL_ID = full_arn.split("/")[-1]
    MAX_TOKENS = 512
    TEMPERATURE = 0.7
    TOP_P = 0.9
    CONTEXT_SIZE = 512 # max length of input
    init_args = dict(model=MODEL_ID, temperature= TEMPERATURE, max_tokens = MAX_TOKENS)
    bedrock_llm = BedrockConverse(botocore_session = botocore_session, **init_args)
    return bedrock_llm