# 团队工作效率评估报告

**时间段**: {{time_period}}

## 团队概况

- **团队规模**: {{team_size}} 人
- **总提交数**: {{total_commits}}
- **平均生产力得分**: {{average_productivity_score|format_score}}
- **平均代码质量得分**: {{average_code_quality_score|format_score}}

## 提交分布

| 成员 | 提交数 | 占比 |
|------|--------|------|
{% for member, commits in commit_distribution.items() %}
| {{member}} | {{commits}} | {{(commits / total_commits * 100)|format_number}}% |
{% endfor %}

## 活跃仓库

{% for repo in top_active_repositories %}
- {{repo}}
{% endfor %}

## 团队优势

{% for strength in team_strengths %}
- {{strength}}
{% endfor %}

## 改进建议

{% for suggestion in improvement_suggestions %}
- {{suggestion}}
{% endfor %}

## 成员表现

| 成员 | 提交数 | 生产力得分 | 代码质量得分 | 主要活跃仓库 |
|------|--------|------------|--------------|--------------|
{% for report in member_reports %}
| {{report.member.name}} | {{report.total_commits}} | {{report.productivity_score|format_score}} | {{report.code_quality_score|format_score}} | {{report.repositories[0] if report.repositories else '-'}} |
{% endfor %}

---

*报告生成时间: {{generated_at}}*