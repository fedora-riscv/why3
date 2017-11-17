# NOTE: Upstream has said that the Frama-C support is still experimental, and
# less functional than the corresponding support in why2.  They recommend not
# enabling it for now.  We abide by their wishes.  Revisit this decision each
# release.

%global opt %(test -x %{_bindir}/ocamlopt && echo 1 || echo 0)
%global tex_dir %{_texmf}/tex/latex

Name:           why3
Version:        0.88.1
Release:        1%{?dist}
Summary:        Software verification platform

# See LICENSE for the terms of the exception
License:        LGPLv2 with exceptions
URL:            http://why3.lri.fr/
Source0:        https://gforge.inria.fr/frs/download.php/file/37185/why3-0.88.1.tar.gz
# Man pages written by Jerry James using text found in the sources.  Hence,
# the copyright and license are the same as for the upstream sources.
Source1:        %{name}-man.tar.xz

BuildRequires:  coq
BuildRequires:  evince
BuildRequires:  flocq
BuildRequires:  gtksourceview2-devel
BuildRequires:  hevea
BuildRequires:  ocaml
BuildRequires:  ocaml-camlp4-devel
BuildRequires:  ocaml-findlib
BuildRequires:  ocaml-lablgtk-devel
BuildRequires:  ocaml-ocamldoc
BuildRequires:  ocaml-ocamlgraph-devel
BuildRequires:  ocaml-menhir-devel
BuildRequires:  ocaml-sqlite-devel
BuildRequires:  ocaml-zarith-devel
BuildRequires:  ocaml-zip-devel
BuildRequires:  rubber
BuildRequires:  tex(comment.sty)
BuildRequires:  tex(upquote.sty)
BuildRequires:  emacs xemacs xemacs-packages-extra

Requires:       gtksourceview2
Requires:       texlive-base
Requires:       vim-filesystem
Provides:       bundled(jquery)

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

%package xemacs
Summary:        XEmacs support file for %{name} files
Requires:       %{name} = %{version}-%{release}
Requires:       xemacs(bin)
BuildArch:      noarch

%description xemacs
This package contains an XEmacs support file for working with %{name} files.

%package all
Summary:        Complete Why3 software verification platform suite
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       alt-ergo coq cvc4 E gappalib-coq z3 zenon

%description all
This package provides a complete software verification platform suite
based on Why3, including various automated and interactive provers.

%prep
%setup -q
%setup -q -T -D -a 1

# Use the correct compiler flags, keep timestamps, and harden the build due to
# network use
# Link the binaries with runtime compiled with -fPIC.
# This avoids many link-time errors.
sed -e "s|-Wall|$RPM_OPT_FLAGS|" \
    -e "s/cp /cp -p /" \
    -e "s|^OLINKFLAGS =.*|& -runtime-variant _pic -ccopt \"$RPM_LD_FLAGS\"|" \
    -i Makefile.in

# Remove spurious executable bits
find -O3 examples -type f -perm /0111 | xargs chmod a-x

%build
%configure --enable-verbose-make
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
mkdir -p %{buildroot}%{tex_dir}/why3
cp -p share/latex/why3lang.sty %{buildroot}%{tex_dir}/why3

# Move the gtksourceview language file to the right place
mkdir -p %{buildroot}%{_datadir}/gtksourceview-2.0
mv %{buildroot}%{_datadir}/%{name}/lang \
   %{buildroot}%{_datadir}/gtksourceview-2.0/language-specs

# Move the vim file to the right place
mkdir -p %{buildroot}%{_datadir}/vim/vimfiles
mv %{buildroot}%{_datadir}/%{name}/vim/ftdetect \
   %{buildroot}%{_datadir}/%{name}/vim/syntax \
   %{buildroot}%{_datadir}/vim/vimfiles

# Byte compile the (X)Emacs support file
mkdir -p %{buildroot}%{_xemacs_sitelispdir}
cp -p %{buildroot}%{_emacs_sitelispdir}/%{name}.el \
   %{buildroot}%{_xemacs_sitelispdir}
pushd %{buildroot}%{_xemacs_sitelispdir}
%{_xemacs_bytecompile} %{name}.el
cd %{buildroot}%{_emacs_sitelispdir}
%{_emacs_bytecompile} %{name}.el
popd

# Remove misplaced documentation
rm -fr %{buildroot}%{_datadir}/doc

# Remove nonfree boomy icons
rm -fr %{buildroot}%{_datadir}/%{name}/images/boomy

# Fix permissions
chmod 0755 %{buildroot}%{_bindir}/* \
           %{buildroot}%{_libdir}/%{name}/commands/* \
           %{buildroot}%{_libdir}/%{name}/coq-tactic/*.cmxs \
           %{buildroot}%{_libdir}/%{name}/plugins/*.cmxs

%files
%doc AUTHORS CHANGES README doc/manual.pdf
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/bash-completion/
%{_datadir}/gtksourceview-2.0/language-specs/%{name}.lang
%{_datadir}/vim/vimfiles/ftdetect/%{name}.vim
%{_datadir}/vim/vimfiles/syntax/%{name}.vim
%{_datadir}/zsh/
%{tex_dir}/why3/
%{_libdir}/%{name}/
%{_mandir}/man1/%{name}*

%files examples
%doc examples

%files emacs
%{_emacs_sitelispdir}/%{name}.el*

%files xemacs
%{_xemacs_sitelispdir}/%{name}.el*

# "why3-all" is a meta-package; it just depends on other packages, so that
# it's easier to install a useful suite of tools.  Thus, it has no files:
%files all

%changelog
* Fri Nov 17 2017 Richard W.M. Jones <rjones@redhat.com> - 0.88.1-1
- New upstream version 0.88.1.
- OCaml 4.06.0 rebuild.

* Sat Oct  7 2017 Jerry James <loganjerry@gmail.com> - 0.88.0-1
- New usptream release

* Thu Oct  5 2017 Jerry James <loganjerry@gmail.com> - 0.87.3-12
- Rebuild for flocq 2.6.0

* Wed Sep 06 2017 Richard W.M. Jones <rjones@redhat.com> - 0.87.3-11
- OCaml 4.05.0 rebuild.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.87.3-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.87.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 27 2017 Richard W.M. Jones <rjones@redhat.com> - 0.87.3-8
- Bump release and rebuild.

* Tue Jun 27 2017 Richard W.M. Jones <rjones@redhat.com> - 0.87.3-7
- Bump release and rebuild.

* Tue Jun 27 2017 Richard W.M. Jones <rjones@redhat.com> - 0.87.3-6
- Bump release and rebuild.

* Tue Jun 27 2017 Richard W.M. Jones <rjones@redhat.com> - 0.87.3-5
- OCaml 4.04.2 rebuild.

* Fri May 12 2017 Richard W.M. Jones <rjones@redhat.com> - 0.87.3-4
- OCaml 4.04.1 rebuild.

* Fri Mar 24 2017 Jerry James <loganjerry@gmail.com> - 0.87.3-3
- Rebuild to fix coq consistency issue

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.87.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Jerry James <loganjerry@gmail.com> - 0.87.3-1
- New upstream release

* Mon Nov 07 2016 Richard W.M. Jones <rjones@redhat.com> - 0.87.2-4
- Rebuild for OCaml 4.04.0.

* Fri Oct 28 2016 Jerry James <loganjerry@gmail.com> - 0.87.2-3
- Rebuild for coq 8.5pl3
- Remove obsolete scriptlets
- Fix install location of why3lang.sty

* Thu Sep 29 2016 Jerry James <loganjerry@gmail.com> - 0.87.2-2
- Rebuild for flocq 2.5.2 and gappalib-coq 1.3.1

* Fri Sep  2 2016 Jerry James <loganjerry@gmail.com> - 0.87.2-1
- New upstream release

* Wed Jul 13 2016 Jerry James <loganjerry@gmail.com> - 0.87.1-2
- Rebuild for coq 8.5pl2

* Wed Jun  1 2016 Jerry James <loganjerry@gmail.com> - 0.87.1-1
- New upstream release

* Fri Apr 22 2016 Jerry James <loganjerry@gmail.com> - 0.87.0-3
- Rebuild for coq 8.5pl1

* Sat Apr 16 2016 Jerry James <loganjerry@gmail.com> - 0.87.0-2
- Rebuild for ocaml-ocamlgraph 1.8.7

* Fri Mar 18 2016 Jerry James <loganjerry@gmail.com> - 0.87.0-1
- New upstream release
- Drop boomy icon removal; upstream no longer ships them

* Fri Feb 12 2016 Jerry James <loganjerry@gmail.com> - 0.86.3-1
- New upstream release
- Use camlp4 in preference to camlp5

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.86.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Nov 25 2015 Jerry James <loganjerry@gmail.com> - 0.86.2-2
- Rebuild for ocaml-zarith 1.4.1 and ocaml-menhir 20151112

* Wed Oct 14 2015 Jerry James <loganjerry@gmail.com> - 0.86.2-1
- New upstream release
- Do not ship the nonfree boomy icons

* Wed Jun 24 2015 Richard W.M. Jones <rjones@redhat.com> - 0.86.1-2
- ocaml-4.02.2 final rebuild.

* Mon Jun 22 2015 Jerry James <loganjerry@gmail.com> - 0.86.1-1
- New upstream release

* Wed Jun 17 2015 Richard W.M. Jones <rjones@redhat.com> - 0.86-2
- ocaml-4.02.2 rebuild.

* Sat May 16 2015 Jerry James <loganjerry@gmail.com> - 0.86-1
- New upstream release

* Sat Apr 11 2015 Jerry James <loganjerry@gmail.com> - 0.85-9
- Rebuild for coq 8.4pl6

* Wed Mar 18 2015 Jerry James <loganjerry@gmail.com> - 0.85-8
- Rebuild for ocaml-ocamlgraph 1.8.6

* Sat Feb 21 2015 Jerry James <loganjerry@gmail.com> - 0.85-7
- Note bundled jquery
- Fix sed expression separators for new RPM_OPT_FLAGS and RPM_LD_FLAGS

* Wed Feb 18 2015 Richard W.M. Jones <rjones@redhat.com> - 0.85-6
- ocaml-4.02.1 rebuild.

* Thu Nov  6 2014 Jerry James <loganjerry@gmail.com> - 0.85-5
- Rebuild for ocaml-camlp5 6.12

* Thu Oct 30 2014 Jerry James <loganjerry@gmail.com> - 0.85-4
- Rebuild for coq 8.4pl5

* Tue Oct 14 2014 Jerry James <loganjerry@gmail.com> - 0.85-3
- Rebuild for ocaml-zarith 1.3

* Thu Sep 18 2014 Jerry James <loganjerry@gmail.com> - 0.85-2
- Bump and rebuild

* Wed Sep 17 2014 Jerry James <loganjerry@gmail.com> - 0.85-1
- New upstream release
- New source URL

* Tue Sep  2 2014 Jerry James <loganjerry@gmail.com> - 0.84-1
- New upstream release
- Fix license handling

* Mon Aug 25 2014 Jerry James <loganjerry@gmail.com> - 0.83-14
- Rebuild for new gappalib-coq build

* Sun Aug 24 2014 Richard W.M. Jones <rjones@redhat.com> - 0.83-13
- ocaml-4.02.0+rc1 rebuild.

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.83-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Aug  4 2014 Jerry James <loganjerry@gmail.com> - 0.83-11
- Rebuild for new gappalib-coq build

* Sat Aug 02 2014 Richard W.M. Jones <rjones@redhat.com> - 0.83-10
- ocaml-4.02.0-0.8.git10e45753.fc22 rebuild.

* Fri Aug 01 2014 Richard W.M. Jones <rjones@redhat.com> - 0.83-9
- OCaml 4.02.0 beta rebuild.

* Thu Jun 26 2014 Jerry James <loganjerry@gmail.com> - 0.83-8
- Linking with -z relro -z now breaks plugins; omit "-z now"

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.83-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 13 2014 Jerry James <loganjerry@gmail.com> - 0.83-6
- Rebuild for coq 8.4pl4

* Mon Apr 21 2014 Jerry James <loganjerry@gmail.com> - 0.83-5
- Rebuild for flocq 2.3.0 and ocamlgraph 1.8.5
- Drop unnecessary sqlite-devel BR

* Tue Apr 15 2014 Richard W.M. Jones <rjones@redhat.com> - 0.83-4
- Remove ocaml_arches macro (RHBZ#1087794).

* Mon Mar 24 2014 Jerry James <loganjerry@gmail.com> - 0.83-3
- Apply upstream fix for building with ocaml-zarith
- Fix file encodings
- Fix permission bits

* Tue Mar 18 2014 Jerry James <loganjerry@gmail.com> - 0.83-2
- Back out the post-release fix to the Coq printer, which breaks Frama-C

* Fri Mar 14 2014 Jerry James <loganjerry@gmail.com> - 0.83-1
- New upstream release
- Use cvc4 instead of cvc3

* Wed Feb 26 2014 Jerry James <loganjerry@gmail.com> - 0.82-2
- Rebuild for ocamlgraph 1.8.4
- BR ocaml-findlib instead of ocaml-findlib-devel

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
