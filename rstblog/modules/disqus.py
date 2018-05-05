# -*- coding: utf-8 -*-
"""
    rstblog.modules.disqus
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements disqus element if asked for.
    
    To use this, include ``disqus`` in the list of modules in your ``config.yml`` file,
    and add a configuration variable to match your settings : ``disqus.shortname`` 
    
    To set developer mode on the site, set ``disqus.developer=1`` in your ``config.yml`` file.
    
    To prevent comments on a particular page, set ``disqus = no`` in the page's YAML preamble.

    :copyright: (c) 2012 by Martin Andrews.
    :license: BSD, see LICENSE for more details.
"""
import jinja2

@jinja2.contextfunction
def get_disqus(context):
    var_shortname=context['builder'].config.root_get('modules.disqus.shortname', 'YOUR-DISQUS-SHORTNAME')

    var_developer=''
    if context['builder'].config.root_get('modules.disqus.developer', False):
        var_developer='var disqus_developer = 1;'
    
    disqus_txt="""
<div id="disqus_thread"></div>
<script>
var disqus_shortname = '%s'; // required: replace example with your forum shortname
%s
/**
*  RECOMMENDED CONFIGURATION VARIABLES: EDIT AND UNCOMMENT THE SECTION BELOW TO INSERT DYNAMIC VALUES FROM YOUR PLATFORM OR CMS.
*  LEARN WHY DEFINING THESE VARIABLES IS IMPORTANT: https://disqus.com/admin/universalcode/#configuration-variables*/
/*
var disqus_config = function () {
this.page.url = PAGE_URL;  // Replace PAGE_URL with your page's canonical URL variable
this.page.identifier = PAGE_IDENTIFIER; // Replace PAGE_IDENTIFIER with your page's unique identifier variable
};
*/
(function() { // DON'T EDIT BELOW THIS LINE
var d = document, s = d.createElement('script');
s.src = 'https://' + disqus_shortname + '.disqus.com/embed.js';
s.setAttribute('data-timestamp', +new Date());
(d.head || d.body).appendChild(s);
})();
</script>
<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
""" % (var_shortname, var_developer)

    if not context['config'].get('disqus', True):
        disqus_txt='' # "<h1>DISQUS DEFEATED</h1>"
        
    return jinja2.Markup(disqus_txt.encode('utf-8'))


def setup(builder):
    builder.jinja_env.globals['get_disqus'] = get_disqus
