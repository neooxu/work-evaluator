# {{member.name}} 工作报表

**时间段**: {{time_period}}

## 工作摘要

- **提交总数**: {{total_commits}}
- **修改文件数**: {{total_files_changed}}
- **添加行数**: {{total_insertions}}
- **删除行数**: {{total_deletions}}
- **活跃仓库**: {{repositories|join(', ')}}

## 效率指标

- **生产力得分**: {{productivity_score|format_score}}
- **代码质量得分**: {{code_quality_score|format_score}}
- **提交频率**: {{commit_frequency|format_number}} 次/天

## 优势

{% for strength in strengths %}
- {{strength}}
{% endfor %}

## 改进领域

{% for area in improvement_areas %}
- {{area}}
{% endfor %}

## 建议

{% for recommendation in recommendations %}
- {{recommendation}}
{% endfor %}

## 提交详情

| 提交ID | 日期 | 仓库 | 消息 | 文件变更 | 添加/删除 |
|--------|------|------|------|----------|-----------|
{% for commit in commits %}
| {{commit.commit_id}} | {{commit.date}} | {{commit.repository}} | {{commit.message}} | {{commit.files_changed}} | +{{commit.insertions}}/-{{commit.deletions}} |
{% endfor %}

---

*报告生成时间: {{generated_at}}*