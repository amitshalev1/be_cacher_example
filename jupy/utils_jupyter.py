from IPython.display import display, Markdown

def get_toc(list_of_titles,name=""):
    '''
    create markdown for the menu and the bullet links
    input:
        list_of_titles=['item 1','item2']
    output:
        dict({'menu':maskdown object containing titles},'item 1':markdown of item...)
    '''
    to_return={'menu':[Markdown(f'[{x}](#{name}_bullet{str(i)})') for i,x in enumerate(list_of_titles)]}
    for i,x in enumerate(list_of_titles):
        to_return[x]=Markdown(f'# {x}<br><a class="anchor" id="{name}_bullet{str(i)}"></a>')
        to_return[i]=Markdown(f'# {x}<br><a class="anchor" id="{name}_bullet{str(i)}"></a>')
    return to_return     
    
class table_of_content:
    '''table of content for jupyter'''

    def __init__(self, name = "",list_of_titles=[]):
        self.name = name
        self.toc=get_toc(list_of_titles,name=self.name)
        
    def display_menu(self):
        '''
        displays a list created by table_of_content
        '''
        display(self.top_anchor)
        for x in self.toc['menu']: display(x)

    def display_item(self,item,include_top=True):
        display(self.toc[item])
        if include_top:
            display(self.top_link)
        
        


    @property
    def top_anchor(self):
        return Markdown(f'<a class="anchor" id="{self.name}top"></a>')

    @property
    def top_link(self):
        return Markdown(f'[top](#{self.name}top)')