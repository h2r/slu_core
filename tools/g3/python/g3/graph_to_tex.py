import os.path
import subprocess
from environ_vars import SLU_HOME

def to_tex_string(ggg):
    output = []
    output.append(r"""
\documentclass{article}

\usepackage[vcentering,dvips]{geometry}
\geometry{papersize={20in,3in},total={20in,3in}}


%\usepackage[EU1]{fontenc}
%\usepackage{mathspec}

%\exchangeforms{phi, gamma}
%\setmainfont[Numbers=OldStyle]{Sabon LT Std}

%\defaultfontfeatures{Scale=MatchLowercase}
%\setmainfont{Liberation Serif}



%\setmathsfont(Digits,Latin)[Scale=MatchLowercase]{Liberation Serif}
%\setmathsfont(Greek)[Scale=MatchLowercase]{OpenSymbol}
%\setmathrm{Liberation Serif}
\usepackage{graphics}
%\usepackage{aaai}
%\usepackage{times}
%\usepackage{helvet}
%\usepackage{courier}
\usepackage{com.braju.graphicalmodels}
\catcode`\@=11%
\begin{document}

\begin{pspicture}(0,0)(20, 6) 
\SpecialCoor

""")
    output.append(to_tex_body(ggg))
    output.append("""
\end{pspicture}
\end{document}""")
    return "".join(output)

def to_tex_body(ggg):
    output = []
    plotted_node_to_id = {}
    lambda_id_to_gamma_nodes = {}
    for i, lambda_node in enumerate(sorted(ggg.lambda_nodes, key=lambda n: ggg.evidence_for_node(n)[0].start)):
        output.append(r"\rput(%.1f, 0.15){\GM@node[observed=true, nodeSize=5mm]{lambda_%d}}" % 
                      (i*3, i))
        output.append(r"""
\GM@label[offset=0.6\GM@nodeSize]{lambda_%d}{\parbox{1\linewidth}{~
\newline
\newline
$\lambda_%d$\newline{ ``%s''}}}""" % (i, i, " ".join(s.text for s in ggg.evidence_for_node(lambda_node))))


        output.append(r"\rput(%.1f, 1){\GM@node[observed=true, nodeSize=5mm]{phi_%d}}" % (i*3 + 1, i))
        output.append(r"\GM@label[offset=0.6\GM@nodeSize,angle=-35]{phi_%d}{$\phi_%d$}" % (i, i))

        output.append(r"\rput(%.1f, 1){\GM@node[query=true, nodeSize=1.25mm]{f_%d}}" % (i*3, i))


        output.append(r"\ncline[arrows=-]{lambda_%d}{f_%d}" % (i, i))
        output.append(r"\ncline[arrows=-]{phi_%d}{f_%d}" % (i, i))



        for factor in lambda_node.factors:
            gamma_nodes = [n for n in factor.nodes if n.is_gamma]
            lambda_id_to_gamma_nodes.setdefault(i, [])
            lambda_id_to_gamma_nodes[i].extend(gamma_nodes)
            for gamma_node in gamma_nodes:
                if factor.link_for_node(gamma_node) == "top":
                    if not gamma_node in plotted_node_to_id:
                        output.append(r"\rput(%.1f, 3){\GM@node[observed=true, nodeSize=5mm]{gamma_%d}}" % (i*3, i))
                        output.append(r"\GM@label[offset=0.6\GM@nodeSize,angle=35]{gamma_%d}{$\gamma_%d$}" % (i, i))
                        plotted_node_to_id[gamma_node] = i
                        
                    gamma_idx = plotted_node_to_id[gamma_node]
                    output.append(r"\ncline[arrows=-]{gamma_%d}{f_%d}" % (gamma_idx, i))
                
                
    for lambda_id, gamma_nodes in lambda_id_to_gamma_nodes.iteritems():
        for gamma_node in gamma_nodes:
            if gamma_node in plotted_node_to_id:
                gamma_idx = plotted_node_to_id[gamma_node]
                output.append(r"\ncline[arrows=-]{gamma_%d}{f_%d}" % (gamma_idx, lambda_id))
        

                    
                    


        
    return "\n".join(output)


def to_tex_file(ggg, pdf_fname):
    basename, ext = os.path.splitext(pdf_fname)
    tex_fname = basename + ".tex"
    
    with open(tex_fname, "w") as f:
        f.write(to_tex_string(ggg))
    for i in range(2):
        subprocess.call("TEXINPUTS_xelatex=%s/tools/g3/tex: latex %s" % 
                        (SLU_HOME, tex_fname), shell=True)
    
