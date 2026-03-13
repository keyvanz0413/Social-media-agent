#!/usr/bin/env python3
"""Manual utility: list available models from configured OpenAI-compatible endpoint."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def main():
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    print("=" * 60)
    print("检查第三方平台支持的模型")
    print(f"平台: {os.getenv('OPENAI_BASE_URL')}")
    print("=" * 60)

    try:
        models = client.models.list()
        print(f"\n✅ 找到 {len(models.data)} 个可用模型：\n")
        for m in sorted(model.id for model in models.data)[:50]:
            print(f"  - {m}")
    except Exception as e:
        print(f"❌ 无法列出模型: {str(e)}")


if __name__ == "__main__":
    main()

