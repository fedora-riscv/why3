# NOTE: Upstream has said that the Frama-C support is still experimental, and
# less functional than the corresponding support in why2.  They recommend not
# enabling it for now.  We abide by their wishes.  Revisit this decision each
# release.

%global opt %(test -x %{_bindir}/ocamlopt && echo 1 || echo 0)
%global texmf_dir %{_datadir}/texmf

Name:           why3
Version:        0.82
Release:        1%{?dist}
Summary:        Software verification platform

# See LICENSE for the terms of the exception
License:        LGPLv2 with exceptions
URL:            http://why3.lri.fr/
Source0:        http://why3.lri.fr/download/%{name}-%{version}.tar.gz
# Man pages written by Jerry James using text found in the sources.  Hence,
# the copyright and license are the same as for the upstream sources.
Source1:        %{name}-man.tar.xz
# Post-release fixes from upstream.  Currently this contains:
# 14ee7f4912d0e18bd5831d56070376d0a5f2330c
#   Add an explicit coercion so that it compiles with both lablgtk 2.16 and
#   2.18.
Patch0:         %{name}-fixes.patch

BuildRequires:  coq
BuildRequires:  evince
BuildRequires:  flocq
BuildRequires:  gtksourceview2-devel
BuildRequires:  hevea
BuildRequires:  ocaml
BuildRequires:  ocaml-camlp5-devel
BuildRequires:  ocaml-findlib-devel
BuildRequires:  ocaml-lablgtk-devel
BuildRequires:  ocaml-ocamldoc
BuildRequires:  ocaml-ocamlgraph-devel
BuildRequires:  ocaml-sqlite-devel
BuildRequires:  rubber
BuildRequires:  sqlite-devel
BuildRequires:  tex(comment.sty)
BuildRequires:  emacs xemacs xemacs-packages-extra

Requires:       gtksourceview2
Requires:       texlive-base
Requires:       vim-filesystem
Requires(posttrans): tex(tex)
Requires(postun): tex(tex)

ExclusiveArch:  %{ocaml_arches}

# The corresponding Provides is not generated, so filter this out
%global __requires_exclude ocaml\\\(Why3\\\)

%description
Why3 is the next generation of the Why software verification platform.
Why3 clearly separates the purely logical specification part from
generation of verification conditions for programs.  It features a rich
library of proof task transformations that can be chained to produce a
suitable input for a large set of theorem provers, including SMT
solvers, TPTP provers, as well as interactive proof assistants.

%package examples
Summary:        Example inputs
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description examples
Example source code with why3 annotations.

%package emacs
Summary:        Emacs support file for %{name} files
Requires:       %{name} = %{version}-%{release}
Requires:       emacs(bin)
BuildArch:      noarch

%description emacs
This package contains an Emacs support file for working with %{name} files.

%package emacs-el
Summary:        Emacs source file for %{name} support
Requires:       %{name}-emacs = %{version}-%{release}
BuildArch:      noarch

%description emacs-el
This package contains the Emacs source file for the Emacs %{name} support.
This package is not needed to use the Emacs support.

%package xemacs
Summary:        XEmacs support file for %{name} files
Requires:       %{name} = %{version}-%{release}
Requires:       xemacs(bin)
BuildArch:      noarch

%description xemacs
This package contains an XEmacs support file for working with %{name} files.

%package xemacs-el
Summary:        XEmacs source file for %{name} support
Requires:       %{name}-xemacs = %{version}-%{release}
BuildArch:      noarch

%description xemacs-el
This package contains the XEmacs source file for the XEmacs %{name} support.
This package is not needed to use the Emacs support.

%package all
Summary:        Complete Why3 software verification platform suite
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       alt-ergo coq cvc3 E gappalib-coq

%description all
This package provides a complete software verification platform suite
based on Why3, including various automated and interactive provers.

%prep
%setup -q
%setup -q -T -D -a 1
%patch0

# Use the correct compiler flags, keep timestamps, and harden the build due to
# network use
sed -e "s/-Wall/$RPM_OPT_FLAGS/" \
    -e "s/cp /cp -p /" \
    -e "s/Aer-29/& -ccopt -Wl,-z,relro,-z,now/" \
    -i Makefile.in

%build
%configure
make #%%{?_smp_mflags}
make doc/manual.pdf

%install
make install DESTDIR=%{buildroot}

# Install the man pages
mkdir -p %{buildroot}%{_mandir}/man1
cd man
for f in *.1; do
  sed "s/@version@/%{version}/" $f > %{buildroot}%{_mandir}/man1/$f
  touch -r $f %{buildroot}%{_mandir}/man1/$f
done
cd ..

# Install the bash completion file
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
cp -p share/bash/%{name} %{buildroot}%{_datadir}/bash-completion/completions

# Install the zsh completion file
mkdir -p %{buildroot}%{_datadir}/zsh/site-functions
cp -p share/zsh/_why3 %{buildroot}%{_datadir}/zsh/site-functions

# Install the LaTeX style
mkdir -p %{buildroot}%{_datadir}/texmf/tex/latex/why3
cp -p share/latex/why3lang.sty %{buildroot}%{_datadir}/texmf/tex/latex/why3

# Move the gtksourceview language file to the right place
mkdir -p %{buildroot}%{_datadir}/gtksourceview-2.0
mv %{buildroot}%{_datadir}/%{name}/lang \
   %{buildroot}%{_datadir}/gtksourceview-2.0/language-specs

# Move the vim file to the right place
mkdir -p %{buildroot}%{_datadir}/vim/vimfiles
mv %{buildroot}%{_datadir}/%{name}/vim \
   %{buildroot}%{_datadir}/vim/vimfiles/syntax

# Move the (X)Emacs support file to the right place and byte compile.
mkdir -p %{buildroot}%{_xemacs_sitelispdir}
cp -p %{buildroot}%{_datadir}/%{name}/emacs/%{name}.el \
   %{buildroot}%{_xemacs_sitelispdir}
pushd %{buildroot}%{_xemacs_sitelispdir}
%{_xemacs_bytecompile} %{name}.el
mkdir -p %{buildroot}%{_emacs_sitelispdir}
mv %{buildroot}%{_datadir}/%{name}/emacs/%{name}.el \
   %{buildroot}%{_emacs_sitelispdir}
rmdir %{buildroot}%{_datadir}/%{name}/emacs
cd %{buildroot}%{_emacs_sitelispdir}
%{_emacs_bytecompile} %{name}.el
popd

# Remove misplaced documentation
rm -fr %{buildroot}%{_datadir}/doc

%post
mktexlsr &> /dev/null || :

%postun
mktexlsr &> /dev/null || :

%files
%doc AUTHORS CHANGES LICENSE README doc/manual.pdf
%{_bindir}/%{name}*
%{_datadir}/%{name}/
%{_datadir}/bash-completion/
%{_datadir}/gtksourceview-2.0/language-specs/%{name}.lang
%{_datadir}/texmf/tex/latex/why3/
%{_datadir}/vim/vimfiles/syntax/%{name}.vim
%{_datadir}/zsh/
%{_libdir}/%{name}/
%{_mandir}/man1/%{name}*

%files examples
%doc examples

%files emacs
%{_emacs_sitelispdir}/%{name}.elc

%files emacs-el
%{_emacs_sitelispdir}/%{name}.el

%files xemacs
%{_xemacs_sitelispdir}/%{name}.elc

%files xemacs-el
%{_xemacs_sitelispdir}/%{name}.el

# "why3-all" is a meta-package; it just depends on other packages, so that
# it's easier to install a useful suite of tools.  Thus, it has no files:
%files all

%changelog
* Fri Dec 13 2013 Jerry James <loganjerry@gmail.com> - 0.82-1
- New upstream release
- Drop upstreamed patches
- Add -examples subpackage
- Install LaTeX style
- Turn off frama-c support at upstream's request

* Mon Sep 30 2013 Jerry James <loganjerry@gmail.com> - 0.81-6
- Apply upstream fix for change in the alt-ergo timelimit option

* Tue Sep 17 2013 Jerry James <loganjerry@gmail.com> - 0.81-5
- Rebuild for OCaml 4.01.0
- Enable debuginfo for the ocaml sources

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.81-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 21 2013 Jerry James <loganjerry@gmail.com> - 0.81-3
- Rebuild for frama-c Fluorine 20130601

* Thu May 23 2013 Jerry James <loganjerry@gmail.com> - 0.81-2
- Rebuild for frama-c Fluorine 20130501

* Fri May 10 2013 Jerry James <loganjerry@gmail.com> - 0.81-1
- New upstream release
- Disable PVS support for now; it requires the NASA libraries
- Fix the conflict between the why and why3 Emacs packages (bz 913522)
- Disable parallel builds due to intermittent build failures

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.73-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan  7 2013 Jerry James <loganjerry@gmail.com> - 0.73-4
- Rebuild for coq 8.4pl1

* Fri Dec 14 2012 Richard W.M. Jones <rjones@redhat.com> - 0.73-3
- Rebuild for OCaml 4.00.1.

* Thu Aug 23 2012 Jerry James <loganjerry@gmail.com> - 0.73-2
- Rebuild for coq 8.4

* Thu Aug  2 2012 Jerry James <loganjerry@gmail.com> - 0.73-1
- New upstream release

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.71-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Apr 19 2012 Jerry James <loganjerry@gmail.com> - 0.71-2
- Add missing sqlite-devel BR
- Do not move the coq plugin
- Generate debuginfo for the sole C program
- Add man pages

* Fri Dec 16 2011 Jerry James <loganjerry@gmail.com> - 0.71-1
- Initial RPM
