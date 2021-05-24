.PHONY: thesis.pdf release clean fig

thesis.pdf:
	latexmk -pdf thesis.tex

fig:
	rm -rf fig
	#python3 -m pdb fig_src/generate_fig.py fig
	fig_src/generate_fig.py fig
	tree fig

release: fig thesis.pdf
	mkdir -p releases
	if git describe --always --dirty | grep dirty ; then echo must not be dirty; exit 1; fi
	releasename="$$(date '+%F')"-"$$(git describe --always --dirty)"; \
		releasefile="releases/thesis-"$$releasename".pdf"; \
		cp --no-clobber thesis.pdf $$releasefile  && \
		git add $$releasefile && \
		git commit -m "release $$releasename"


clean:
	latexmk -C
