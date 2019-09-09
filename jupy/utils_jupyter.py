from IPython.display import display, Markdown

def get_toc(list_of_titles):
    '''
    create markdown for the menu and the bullet links
    input:
        list_of_titles=['item 1','item2']
    output:
        dict({'menu':maskdown object containing titles},'item 1':markdown of item...)
    '''
    to_return={'menu':[Markdown('['+x+'](#bullet'+str(i)+')') for i,x in enumerate(list_of_titles)]}
    for i,x in enumerate(list_of_titles):
        to_return[x]=Markdown('# '+x+'<br><a class="anchor" id="bullet'+str(i)+'"></a>')
        to_return[i]=Markdown('# '+x+'<br><a class="anchor" id="bullet'+str(i)+'"></a>')
    return to_return     
    
class table_of_content:
    '''table of content for jupyter'''

    def __init__(self, list_of_titles=[]):
        self.toc=get_toc(list_of_titles)
        
    def display_menu(self):
        '''
        displays a list created by table_of_content
        '''
        display(self.top_anchor)
        for x in self.toc['menu']: display(x)

    def display_item(self,item):
        display(self.toc[item])
        display(self.top_link)
        
        


    @property
    def top_anchor(self):
        return Markdown('<a class="anchor" id="top"></a>')

    @property
    def top_link(self):
        return Markdown('[top](#top)')