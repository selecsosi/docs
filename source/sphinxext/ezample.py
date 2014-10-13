# Directive for embedding code examples

from docutils import nodes

from sphinx.directives.code import CodeBlock
from sphinx.util.compat import Directive, make_admonition


class EzampleSnippet(Directive):    # Params: title, language
    """
    A code snippet in a language.
    """

    has_content = True
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        title = self.arguments[0]
        language = self.arguments[1]

        env = self.state.document.settings.env

        if not hasattr(env, 'ezample_all'):
            env.ezample_all = []
        env.ezample_all.append({
            'docname': env.docname,
            'title': title,
            'langugage': language,
            'content': self.content
        })


class EzampleBlock(Directive):  # Param: title, prints all snippets related to that title
    pass


class ezample_block(nodes.General, nodes.Element):
    pass


def purge_ezamples(app, env, docname):
    if not hasattr(env, 'ezample_all'):
        return
    env.ezample_all = [ezample for ezample in env.ezample_all
                       if ezample['docname'] != docname]

# TODO: (ha) translate this from todo example to this extension
def process_todo_nodes(app, doctree, fromdocname):
    if not app.config.todo_include_todos:
        for node in doctree.traverse(todo):
            node.parent.remove(node)

    # Replace all todolist nodes with a list of the collected todos.
    # Augment each todo with a backlink to the original location.
    env = app.builder.env

    for node in doctree.traverse(todolist):
        if not app.config.todo_include_todos:
            node.replace_self([])
            continue

        content = []

        for todo_info in env.todo_all_todos:
            para = nodes.paragraph()
            filename = env.doc2path(todo_info['docname'], base=None)
            description = (
                _('(The original entry is located in %s, line %d and can be found ') %
                (filename, todo_info['lineno']))
            para += nodes.Text(description, description)

            # Create a reference
            newnode = nodes.reference('', '')
            innernode = nodes.emphasis(_('here'), _('here'))
            newnode['refdocname'] = todo_info['docname']
            newnode['refuri'] = app.builder.get_relative_uri(
                fromdocname, todo_info['docname'])
            newnode['refuri'] += '#' + todo_info['target']['refid']
            newnode.append(innernode)
            para += newnode
            para += nodes.Text('.)', '.)')

            # Insert into the todolist
            content.append(todo_info['todo'])
            content.append(para)

        node.replace_self(content)


def setup(app):
    app.add_node(ezample_block)    # TODO: add visit/depart functions for Theme hooks

    app.add_directive('ezample', EzampleBlock)
    app.add_directive('ezample-snippet', EzampleSnippet)

    app.connect('env-purge-doc', purge_ezamples)
    app.connect('doctree-resolved', resolve_ezamples)
