#!/usr/bin/env python3
"""
预处理 Markdown 文件，将 Hugo shortcode 转换为 Pandoc 可识别的格式

处理两种 shortcode：
1. {{< figure src="/fig/xxx.png" caption="xxx" >}} → ![xxx](static/fig/xxx.png)
2. {{< figure ... >}} (无 src) → 移除（通常用于代码示例）
"""

import re
import sys
import os
from pathlib import Path

def convert_figure_shortcode(text):
    """
    转换 Hugo figure shortcode 为 Markdown 图片语法

    Args:
        text: Markdown 文本内容

    Returns:
        转换后的文本
    """

    # 先处理有 caption 的 figure shortcode
    # 例如: {{< figure src="/fig/ddia_0302.png" caption="图 3-2. xxx" >}}
    pattern_with_caption = r'\{\{< figure\s+src="([^"]+)"[^>]*\scaption="([^"]*)"[^>]*>\}\}'

    def replace_with_caption(match):
        src = match.group(1)
        caption = match.group(2)

        # 移除开头的斜杠，添加 static 前缀
        if src.startswith('/'):
            src = 'static' + src

        # 返回 Markdown 图片语法
        return f'![{caption}]({src})'

    text = re.sub(pattern_with_caption, replace_with_caption, text)

    # 再处理没有 caption 的 figure shortcode
    pattern_without_caption = r'\{\{< figure\s+src="([^"]+)"[^>]*>\}\}'

    def replace_without_caption(match):
        src = match.group(1)

        if src.startswith('/'):
            src = 'static' + src

        return f'[]({src})'

    text = re.sub(pattern_without_caption, replace_without_caption, text)

    # 移除完全没有 src 属性的 figure shortcode（例如用于代码块的）
    pattern_no_src = r'\{\{< figure[^>]*>\}\}'
    text = re.sub(pattern_no_src, '', text)

    return text

def process_file(input_path, output_path):
    """
    处理单个 Markdown 文件

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 转换内容
    converted_content = convert_figure_shortcode(content)

    # 写入输出文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(converted_content)

    print(f"Processed: {input_path} -> {output_path}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: preprocess.py <input_file> [output_file]")
        print("   or: preprocess.py <input_dir> <output_dir>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        # 处理单个文件
        output_path = sys.argv[2] if len(sys.argv) > 2 else input_path
        process_file(input_path, output_path)
    elif os.path.isdir(input_path):
        # 处理目录
        output_dir = sys.argv[2]
        input_dir = Path(input_path)

        # 获取所有 .md 文件
        md_files = list(input_dir.glob('*.md'))

        for md_file in md_files:
            output_file = os.path.join(output_dir, md_file.name)
            process_file(str(md_file), output_file)

        print(f"\nTotal processed: {len(md_files)} files")
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main()
