#!/usr/bin/env python3
"""
预处理 Markdown 文件，将 Hugo shortcode 转换为 Pandoc 可识别的格式

处理两种 shortcode：
1. {{< figure src="/fig/xxx.png" caption="xxx" >}} → ![xxx](static/fig/xxx.png)
2. {{< figure ... >}} (无 src) → 移除（通常用于代码示例）
"""

import os
import re
import sys
from pathlib import Path

FIGURE_SHORTCODE_RE = re.compile(r"\{\{<\s*figure\b(.*?)>\}\}", re.DOTALL)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
ABS_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(/(?!static/)([^)]+)\)')


def _escape_alt_text(text):
    """Escape `]` in alt text to avoid breaking Markdown image syntax."""
    return text.replace("]", r"\]")


def convert_markdown(text):
    """
    转换 Hugo figure shortcode 和绝对路径图片引用。

    Args:
        text: Markdown 文本内容

    Returns:
        转换后的文本
    """
    def replace_figure_shortcode(match):
        attrs_text = match.group(1)
        attrs = dict(ATTR_RE.findall(attrs_text))
        src = attrs.get("src")

        # 没有 src 的 figure 一般是代码示例占位，直接移除
        if not src:
            return ""

        # 绝对路径资源转为相对 static 路径，便于 Pandoc 打包
        if src.startswith('/'):
            src = 'static' + src

        # 优先 caption，fallback 到 title，至少保证图片可渲染
        alt = _escape_alt_text(attrs.get("caption") or attrs.get("title") or "")
        return f'![{alt}]({src})'

    text = FIGURE_SHORTCODE_RE.sub(replace_figure_shortcode, text)

    # 把 Markdown 里的绝对路径图片 ![](/map/ch01.png) 转为 static/map/ch01.png
    text = ABS_IMAGE_RE.sub(r'![\1](static/\2)', text)

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
    converted_content = convert_markdown(content)

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
        md_files = sorted(input_dir.glob('*.md'))

        for md_file in md_files:
            output_file = os.path.join(output_dir, md_file.name)
            process_file(str(md_file), output_file)

        print(f"\nTotal processed: {len(md_files)} files")
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main()
