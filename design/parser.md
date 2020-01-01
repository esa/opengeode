These notes explain how to load a model and render it as a statechart

This can be done for example using ptpython3


    # Import the opengeode library to access the parser
    import opengeode

    # Make sure Qt is initialized to render the model
    app = opengeode.init_qt()

    # Parse a model
    ast, _, _ = opengeode.ogParser.parse_pr(['model.pr'])

    # ast is of type opengeode.ogAST.AST (check ogAST.py)

    # Extract the SDL process
    process = ast.processes[0]  # type: opengeode.ogAST.Process

    # Create a scene and a view to render the process as a statechart
    scene = opengeode.SDL_Scene('statechart')
    view = opengeode.SDL_View(scene)

    # Transform the AST of the process into a graphviz graph
    graph = opengeode.Statechart.create_dot_graph(process, basic=True)
  
    # Then render the graph (requires graphviz)
    opengeode.Statechart.render_statechart(scene, graph)

    # Enable the view and run the application
    view.show()
    app.exec_()








