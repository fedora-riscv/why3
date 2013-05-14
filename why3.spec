# Debuginfo cannot be generated usefully for OCaml programs, so the only
# debuginfo for this package is for the sole C program: why3-cpulimit.

%global opt %(test -x %{_bindir}/ocamlopt && echo 1 || echo 0)

Name:           why3
Version:        0.81
Release:        1%{?dist}
Summary:        Software verification platform

License:        LGPLv2 with exceptions
URL:            http://why3.lri.fr/
Source0:        http://why3.lri.fr/download/%{name}-%{version}.tar.gz
# Man pages written by Jerry James using text found in the sources.  Hence,
# the copyright and license are the same as for the upstream sources.
Source1:        %{name}-man.tar.xz
# Post-release fixes from upstream.  Currently this contains:
# bbafe47e7569fc6106bc5e5f03ec2eba7ff6534a
#    [emacs] why.el renamed to why3.el
#    [GTK sourceview] why.lang renamed to why3.lang
# 666aeb684a11a017b795469447bdeae13dc009b7
#    fixed eliminate_inductive with let-in
# 2b88812f1ac8413bf4b5988453379e4f2341afaf
#    Update Jessie3 plugin to Frama-C Fluorine.
Patch0:         %{name}-fixes.patch

BuildRequires:  coq
BuildRequires:  evince
BuildRequires:  flocq
BuildRequires:  frama-c
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
BuildRequires:  emacs xemacs xemacs-packages-extra

Requires:       frama-c
Requires:       gtksourceview2
Requires:       vim-filesystem

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
%configure --enable-frama-c
make #%%{?_smp_mflags}

# The Makefile does not strip the tactics and plugins
find . -name \*.cmxs | xargs strip

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

%files
%doc AUTHORS CHANGES LICENSE README doc/manual.pdf
%{_bindir}/%{name}*
%{_datadir}/%{name}/
%{_datadir}/bash-completion/
%{_datadir}/gtksourceview-2.0/language-specs/%{name}.lang
%{_datadir}/vim/vimfiles/syntax/%{name}.vim
%{_datadir}/zsh/
%{_libdir}/frama-c/plugins/Jessie3.*
%{_libdir}/%{name}/
%{_mandir}/man1/%{name}*

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
