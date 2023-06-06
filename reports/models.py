from django.db import models

# Create your models here.
"""
class ReportUser(CommonModel):
    '''유저 신고
    status={1:처리 안됨,2:해결됨}
        '''
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported')
    report_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name)
"""

"""
class ReportUser(CommonModel):
    '''유저 신고
    status={1:처리 안됨,2:해결됨}
        '''
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported')
"""

"""
class ReportArticle(CommonModel):
    '''유저 신고
    status={1:처리 안됨,2:해결됨}
        '''
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reported')
"""

"""
class ReportArticle(CommonModel):
    '''유저 신고
    status={1:처리 안됨,2:해결됨}
        '''
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reported')
"""

"""
class ReportComment(CommonModel):
    '''유저 신고
    status={1:처리 안됨,2:해결됨}
        '''
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reported')
"""