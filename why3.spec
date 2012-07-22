# Debuginfo cannot be generated usefully for OCaml programs, so the only
# debuginfo for this package is for the sole C program: why3-cpulimit.

%global opt %(test -x %{_bindir}/ocamlopt && echo 1 || echo 0)

Name:           why3
Version:        0.71
Release:        3%{?dist}
Summary:        Software verification platform

License:        LGPLv2 with exceptions
URL:            http://why3.lri.fr/
Source0:        https://gforge.inria.fr/frs/download.php/29252/%{name}-%{version}.tar.gz
# Man pages written by Jerry James using text found in the sources.  Hence,
# the copyright and license are the same as for the upstream sources.
Source1:        %{name}-man.tar.xz
# This patch will not be upstream.  It updates the expected version numbers of
# some components to match the currently available Fedora versions.
Patch0:         %{name}-versions.patch

BuildRequires:  coq
BuildRequires:  evince
BuildRequires:  gtksourceview2-devel
BuildRequires:  ocaml
BuildRequires:  ocaml-camlp5-devel
BuildRequires:  ocaml-findlib-devel
BuildRequires:  ocaml-lablgtk-devel
BuildRequires:  ocaml-menhir-devel
BuildRequires:  ocaml-ocamldoc
BuildRequires:  ocaml-ocamlgraph-devel
BuildRequires:  ocaml-sqlite-devel
BuildRequires:  rubber
BuildRequires:  sqlite-devel
BuildRequires:  emacs xemacs xemacs-packages-extra

Requires:       gtksourceview2

ExclusiveArch:  %{ocaml_arches}

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
Obsoletes:      why-emacs < 2.31
Provides:       why-emacs = 2.31-1

%description emacs
This package contains an Emacs support file for working with %{name} files.

%package emacs-el
Summary:        Emacs source file for %{name} support
Requires:       %{name}-emacs = %{version}-%{release}
BuildArch:      noarch
Obsoletes:      why-emacs-el < 2.31
Provides:       why-emacs-el = 2.31-1

%description emacs-el
This package contains the Emacs source file for the Emacs %{name} support.
This package is not needed to use the Emacs support.

%package xemacs
Summary:        XEmacs support file for %{name} files
Requires:       %{name} = %{version}-%{release}
Requires:       xemacs(bin)
BuildArch:      noarch
Obsoletes:      why-xemacs < 2.31
Provides:       why-xemacs = 2.31-1

%description xemacs
This package contains an XEmacs support file for working with %{name} files.

%package xemacs-el
Summary:        XEmacs source file for %{name} support
Requires:       %{name}-xemacs = %{version}-%{release}
BuildArch:      noarch
Obsoletes:      why-xemacs-el < 2.31
Provides:       why-xemacs-el = 2.31-1

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

# Use the correct compiler flags and fix linking the TPTP plugin
sed -e "s|-Wall|$RPM_OPT_FLAGS|" \
    -e "s|-shared -o \$@|& \$(MENHIRLIB).cmx|" \
    -i Makefile.in

%build
%configure --enable-menhirlib --enable-doc

make %{?_smp_mflags}

# The makefile doesn't strip the Coq plugin
strip plugins/whytptp.cmxs

%install
make install DESTDIR=$RPM_BUILD_ROOT

# Install the man pages
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
cd man
for f in *.1; do
  sed "s/@version@/%{version}/" $f > $RPM_BUILD_ROOT%{_mandir}/man1/$f
  touch -r $f $RPM_BUILD_ROOT%{_mandir}/man1/$f
done
cd ..

# Move the gtksourceview language file to the right place
mkdir -p $RPM_BUILD_ROOT%{_datadir}/gtksourceview-2.0/language-specs
mv $RPM_BUILD_ROOT%{_datadir}/%{name}/lang/why.lang \
   $RPM_BUILD_ROOT%{_datadir}/gtksourceview-2.0/language-specs
rmdir $RPM_BUILD_ROOT%{_datadir}/%{name}/lang

# Move the (X)Emacs support file to the right place and byte compile.
mkdir -p $RPM_BUILD_ROOT%{_xemacs_sitelispdir}
cp -p $RPM_BUILD_ROOT%{_datadir}/%{name}/emacs/why.el \
   $RPM_BUILD_ROOT%{_xemacs_sitelispdir}
pushd $RPM_BUILD_ROOT%{_xemacs_sitelispdir}
%{_xemacs_bytecompile} why.el
mkdir -p $RPM_BUILD_ROOT%{_emacs_sitelispdir}
mv $RPM_BUILD_ROOT%{_datadir}/%{name}/emacs/why.el \
   $RPM_BUILD_ROOT%{_emacs_sitelispdir}
rmdir $RPM_BUILD_ROOT%{_datadir}/%{name}/emacs
cd $RPM_BUILD_ROOT%{_emacs_sitelispdir}
%{_emacs_bytecompile} why.el
popd

%files
%doc LICENSE README doc/manual.pdf
%{_bindir}/%{name}*
%{_datadir}/%{name}/
%{_datadir}/gtksourceview-2.0/language-specs/why.lang
%{_libdir}/%{name}/
%{_mandir}/man1/%{name}*

%files emacs
%{_emacs_sitelispdir}/why.elc

%files emacs-el
%{_emacs_sitelispdir}/why.el

%files xemacs
%{_xemacs_sitelispdir}/why.elc

%files xemacs-el
%{_xemacs_sitelispdir}/why.el

# "why3-all" is a meta-package; it just depends on other packages, so that
# it's easier to install a useful suite of tools.  Thus, it has no files:
%files all

%changelog
* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.71-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Apr 19 2012 Jerry James <loganjerry@gmail.com> - 0.71-2
- Add missing sqlite-devel BR
- Do not move the coq plugin
- Generate debuginfo for the sole C program
- Add man pages

* Fri Dec 16 2011 Jerry James <loganjerry@gmail.com> - 0.71-1
- Initial RPM
