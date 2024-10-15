# -*- coding: utf-8 -*-
"""
    obsidian_2_markdown_book.py
    ~~~~~~~

    将 obsidian 的文件转换成 markdown book 格式的文件

    用法:
    python obsidian_2_markdown_book.py -i [输入文件路径] -o [输出目录路径]

    :author: fatedeity
    :copyright: (c) 2024, fatedeity
    :date created: 2024-10-14
"""

import os
import re
import shutil

import click


def copy_file_content(source_file: str, target_file: str):
    """
    复制文件内容
    :param source_file:
    :param target_file:
    :return:
    """
    source_dir = os.path.dirname(source_file)
    # 将 target_file 的父目录作为导出目录
    output_dir = os.path.dirname(target_file)
    if not os.path.exists(output_dir):
        # 目录不存在，创建目录
        os.makedirs(output_dir)

    new_lines = []
    # 移除 frontmatter 内容，增加 1 级标题，复制附带的附件
    with open(source_file, 'r') as f:
        is_frontmatter = False
        skip_frontmatter = False
        for line in f:
            # 移除 frontmatter 内容
            if not skip_frontmatter:
                if not is_frontmatter and line.startswith('---'):
                    is_frontmatter = True
                    continue
                elif is_frontmatter and line.startswith('---'):
                    is_frontmatter = False
                    skip_frontmatter = True
                    continue
                elif is_frontmatter:
                    if line.startswith('title'):
                        new_lines.append('# ' + line.split(':')[1].strip() + '\n')
                    continue
            # 检测是否有图片链接
            if line.startswith('!'):
                # 提取图片链接
                inline_links = re.findall(r'!\[.*?\]\(([^)]+)\)', line)
                file_link = inline_links[0]
                attachment_dir = os.path.dirname(os.path.abspath(os.path.join(output_dir, file_link)))
                if not os.path.exists(attachment_dir):
                    # 目录不存在，创建目录
                    os.makedirs(attachment_dir)
                # 复制图片
                shutil.copy(os.path.join(source_dir, file_link), os.path.join(output_dir, file_link))
            new_lines.append(line)
    # 将文件内容写到新的文件里
    with open(target_file, 'w') as f:
        f.writelines(new_lines)


@click.command()
@click.option('--input_file', '-i', help='输入文件路径')
@click.option('--output_dir', '-o', help='输出目录路径')
def main(input_file: str, output_dir: str):
    """
    将 obsidian 的文件转换成 markdown book 格式的文件
    :param input_file:
    :param output_dir:
    :return:
    """
    # 移除 output_dir 路径下的 markdown 文件
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.md'):
                    os.remove(os.path.join(root, file))

    new_lines = []
    # 将 input 作为 README.md 文件，将文件转换成 markdown book 格式的文件
    with open(input_file, 'r') as f:
        is_frontmatter = False
        skip_frontmatter = False
        for line in f:
            # 移除 frontmatter 内容
            if not skip_frontmatter:
                if not is_frontmatter and line.startswith('---'):
                    is_frontmatter = True
                    continue
                elif is_frontmatter and line.startswith('---'):
                    is_frontmatter = False
                    skip_frontmatter = True
                    continue
                elif is_frontmatter:
                    if line.startswith('title'):
                        new_lines.append('# ' + line.split(':')[1].strip() + '\n')
                    continue
            # 列表格式: - 章节名: [源文件名称](源文件链接)
            if line.startswith('- '):
                # 章节名
                target_filename = line[2:].split(':')[0].strip() + '.md'
                # 源文件链接
                source_file_md_text = line[2:].split(':')[1].strip()
                # 只保留文件链接
                line = '- ' + source_file_md_text + '\n'
                inline_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', source_file_md_text)
                file_link = inline_links[0][1]
                # 复制文件内容
                copy_file_content(
                    os.path.join(os.path.dirname(input_file), file_link),
                    os.path.join(output_dir, target_filename),
                )
                new_file_link = os.path.relpath(os.path.join(output_dir, target_filename), output_dir)
                new_lines.append(line.replace(file_link, new_file_link))
            else:
                new_lines.append(line)

    # 将文件内容写到新的文件里
    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.writelines(new_lines)


if __name__ == '__main__':
    main()
