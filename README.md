# RZ Docs


## Install Python 3

Download and Install Python 3.6+ from here https://www.python.org/downloads/


## Install PIP

Run the following cmds

    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py

Or Follow the docs from https://pip.pypa.io/en/stable/installing/


## Install RZ Docs

    pip3 install https://github.com/roanuz/rzdocs/archive/master.zip

## Run Preview
Goto the docs folder and run the following cmd

    rzdocs preview


## Using Flask render function

    from rzdocs.render import render_doc_from_json

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>/')
    def home(path=None):
        return render_doc_from_json(path, base_path='jsons')



# Understanding Markdown
Refer the following links to get started with markdown

https://blog.ghost.org/markdown/


## Inserting snippets

```json
{!_snippets/hello.json!}
```

## Markdown Extensions 
Following markdown extensions are supported

- https://python-markdown.github.io/extensions/meta_data/
- https://python-markdown.github.io/extensions/fenced_code_blocks/
- https://python-markdown.github.io/extensions/attr_list/
- https://python-markdown.github.io/extensions/tables/
- https://github.com/cmacmackin/markdown-include

