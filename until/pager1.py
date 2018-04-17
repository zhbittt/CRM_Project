import  copy
class Pagination(object):
    '''
    分页

        使用：

        context : [ a,b,c,d,e,f,g ]
        request.GET.get("page")  :  http://127.0.0.1:8001/stark/app01/author/?page=7
        request.path_info : /stark/app01/author/

        from until.pager1 import Pagination
        in views:
            pager_obj = Pagination(request.GET.get("page"),len(context),request.path_info)
            context_list = context[pager_obj.start:pager_obj.end]
            page_html_list=pager_obj.page_html()

        in template:
            <nav aria-label="...">
                <ul class="pagination">
                    {% for page_html in page_html_list %}
                        {{ page_html|safe }}
                    {% endfor %}
                </ul>
            </nav>
    '''
    def __init__(self,config,total_count,base_url,max_pager_count=7,per_page_count=10):
        self.request = config.request
        current_page =self.request.GET.get("page","")
        params = copy.deepcopy(self.request.GET)
        params.mutable=True
        if current_page:
            params.pop("page")
        self.params_urlencode = params.urlencode()
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        #url
        self.base_url=base_url

        #当前页码
        self.current_page = current_page

        # 显示11个页码
        self.max_pager_count =max_pager_count

        #数据总条数
        self.total_count =total_count

        #页面显示数据的数量
        self.per_page_count= per_page_count

        #数据最多可显示页数
        self.max_page_num, div = divmod(total_count, per_page_count)
        if div:
            self.max_page_num += 1

        self.half_max_pager_count = int((max_pager_count - 1) / 2)
    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    def page_html(self):
        if self.max_page_num <= self.max_pager_count:
            pager_start = 1
            pager_end = self.max_page_num
        else:
            if self.current_page <= self.half_max_pager_count:
                pager_start = 1
                pager_end = self.max_pager_count
            else:
                if self.current_page + self.half_max_pager_count >= self.max_page_num:
                    pager_start = self.max_page_num - self.max_pager_count + 1
                    pager_end = self.max_page_num
                else:
                    pager_start = self.current_page - self.half_max_pager_count
                    pager_end = self.current_page + self.half_max_pager_count

        #列面列表
        page_html_list = []

        #首页
        page_html_list.append('<li><a href="%s?page=1&%s" aria-label="Previous"><span aria-hidden="true">首页</span></a></li>'%(self.base_url,self.params_urlencode))
        #上一页
        if self.current_page == pager_start:
            left='<li><span><span aria-hidden="true">&laquo;</span></span></li>'
        else:
            left = '<li><a href="%s?page=%s&%s" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>' % (self.base_url, self.current_page-1,self.params_urlencode)
        page_html_list.append(left)

        #页面
        for x in range(pager_start, pager_end + 1):
            if self.current_page == x:
                temp = '<li class="active"><span><span aria-hidden="true">%s</span></span></li>'%x
            else:
                temp = '<li><a href="%s?page=%s&%s" aria-label="Previous"><span aria-hidden="true">%s</span></a></li>'%(self.base_url,x,self.params_urlencode,x)
            page_html_list.append(temp)

        #下一页
        if self.current_page == pager_end:
            right='<li><span><span aria-hidden="true">&raquo;</span></span></li>'
        else:
            right = '<li><a href="%s?page=%s&%s" aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>' % (self.base_url, self.current_page+1,self.params_urlencode)
        page_html_list.append(right)
        #尾页
        page_html_list.append('<li><a href="%s?page=%s&%s" aria-label="Previous"><span aria-hidden="true">尾页</span></a></li>' %(self.base_url,self.max_page_num,self.params_urlencode))
        return page_html_list

