Name:		gnome-bluetooth
Version:	2.28.6
Release:	8%{?dist}
Summary:	Bluetooth graphical utilities

Group:		Applications/Communications
License:	GPLv2+
URL:		http://live.gnome.org/GnomeBluetooth
Source0:	http://download.gnome.org/sources/gnome-bluetooth/2.28/gnome-bluetooth-%{version}.tar.bz2
Source1:	61-gnome-bluetooth-rfkill.rules
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
ExcludeArch:	s390 s390x

BuildRequires:	gtk2-devel
BuildRequires:	GConf2-devel
BuildRequires:	dbus-glib-devel
BuildRequires:	hal-devel
BuildRequires:	unique-devel
BuildRequires:	libnotify-devel
BuildRequires:	gnome-doc-utils

BuildRequires:	intltool desktop-file-utils gettext gtk-doc

Obsoletes:	bluez-pin
Provides:	dbus-bluez-pin-helper
Conflicts:	bluez-gnome <= 1.8
Obsoletes:	bluez-gnome <= 1.8

# Otherwise we might end up with mismatching version
Requires:	%{name}-libs = %{version}-%{release}
Requires:	gvfs-obexftp
Requires:	bluez >= 4.42
Requires:	obexd
Requires:	desktop-notification-daemon
Requires:	pulseaudio-module-bluetooth

Requires(post):		desktop-file-utils
Requires(postun):	desktop-file-utils

# updated translations
# https://bugzilla.redhat.com/show_bug.cgi?id=589198
Patch0: gnome-bluetooth-translations.patch

# Upstream patches
Patch1: 0001-Make-bluetooth_type_to_string-return-a-translated-st.patch
Patch2: 0001-Update-the-bluetooth-sendto-man-page.patch
Patch3: 0001-Fix-run-time-warning.patch
Patch4: 0001-Avoid-getting-killswitch-page-when-hard-blocked.patch
Patch9: 0001-Better-debug-for-killswitch-code.patch
Patch10: 0001-Even-better-killswitch-debugging.patch
Patch5: 0001-Try-to-merge-killswitch-changed-events.patch
Patch6: 0001-Fix-adapter-not-going-powered-when-coming-back-from-.patch
Patch7: 0001-Add-guards-to-BluetoothAgent-functions.patch
Patch8: 0001-Fix-compilation-warning-for-last-commit.patch
Patch11: 0001-Work-around-GTK-bug-not-showing-status-icon.patch
Patch12: 0002-Make-sure-the-icon-is-shown-hidden-when-killswitch-c.patch
Patch13: 0003-Make-sure-all-the-unblocked-adapters-are-powered.patch


%description
The gnome-bluetooth package contains graphical utilities to setup,
monitor and use Bluetooth devices.

%package libs
Summary:	GTK+ Bluetooth device selection widgets
Group:		System Environment/Libraries
License:	LGPLv2+

%description libs
This package contains libraries needed for applications that
want to display a Bluetooth device selection widget.

%package libs-devel
Summary:	Development files for %{name}-libs
Group:		Development/Libraries
License:	LGPLv2+
Requires:	%{name}-libs = %{version}-%{release}
Requires:	gtk-doc pkgconfig
Obsoletes:	gnome-bluetooth-devel < 2.27.1-4
Provides:	gnome-bluetooth-devel = %{version}

%description libs-devel
This package contains the libraries amd header files that are needed
for writing applications that require a Bluetooth device selection widget.

%prep
%setup -q -n gnome-bluetooth-%{version}
%patch0 -p1 -b .translations
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch9 -p1
%patch10 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1

%build
%configure --disable-desktop-update --disable-icon-update

# FIXME
# make %{?_smp_mflags}
make

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/libgnome-bluetooth.la $RPM_BUILD_ROOT/%{_libdir}/gnome-bluetooth/plugins/*.la

desktop-file-install --vendor=""				\
	--delete-original					\
	--dir=$RPM_BUILD_ROOT%{_datadir}/applications		\
	$RPM_BUILD_ROOT%{_datadir}/applications/bluetooth-properties.desktop

desktop-file-install --vendor=""				\
	--delete-original					\
	--dir=$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/	\
	$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/bluetooth-applet.desktop

install -m0644 -D %{SOURCE1} $RPM_BUILD_ROOT/lib/udev/rules.d/61-gnome-bluetooth-rfkill.rules

# gnome-bluetooth2 is the name for the gettext domain,
# gnome-bluetooth is the name in the docs
%find_lang gnome-bluetooth2
%find_lang %{name} --with-gnome
cat %{name}.lang >> gnome-bluetooth2.lang

# save space by linking identical images in translated docs
helpdir=$RPM_BUILD_ROOT%{_datadir}/gnome/help/%{name}
for f in $helpdir/C/figures/*.png; do
  b="$(basename $f)"
  for d in $helpdir/*; do
    if [ -d "$d" -a "$d" != "$helpdir/C" ]; then
      g="$d/figures/$b"
      if [ -f "$g" ]; then
        if cmp -s $f $g; then
          rm "$g"; ln -s "../../C/figures/$b" "$g"
        fi
      fi
    fi
  done
done

%clean
rm -rf $RPM_BUILD_ROOT

%post
update-desktop-database -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule					\
	%{_sysconfdir}/gconf/schemas/bluetooth-manager.schemas		\
	>& /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	if [ -f %{_sysconfdir}/gconf/schemas/gnome-obex-server.schemas ] ; then
		gconftool-2 --makefile-uninstall-rule \
		%{_sysconfdir}/gconf/schemas/gnome-obex-server.schemas >/dev/null || :
	fi
	if [ -f %{_sysconfdir}/gconf/schemas/bluetooth-manager.schemas ] ; then
		gconftool-2 --makefile-uninstall-rule 				\
		%{_sysconfdir}/gconf/schemas/bluetooth-manager.schemas		\
		>& /dev/null || :
	fi
fi

%preun
if [ "$1" -eq 0 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	if [ -f %{_sysconfdir}/gconf/schemas/gnome-obex-server.schemas ] ; then
		gconftool-2 --makefile-uninstall-rule \
		%{_sysconfdir}/gconf/schemas/gnome-obex-server.schemas > /dev/null || :
	fi
	if [ -f %{_sysconfdir}/gconf/schemas/bluetooth-manager.schemas ] ; then
		gconftool-2 --makefile-uninstall-rule 				\
		%{_sysconfdir}/gconf/schemas/bluetooth-manager.schemas		\
		>& /dev/null || :
	fi
fi

%postun
update-desktop-database -q
if [ $1 -eq 0 ] ; then
	touch --no-create %{_datadir}/icons/hicolor &>/dev/null
	gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%post libs
/sbin/ldconfig
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%posttrans libs
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%postun libs
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
	touch --no-create %{_datadir}/icons/hicolor &>/dev/null
	gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%files -f gnome-bluetooth2.lang
%defattr(-,root,root,-)
%doc README NEWS COPYING
%{_sysconfdir}/gconf/schemas/bluetooth-manager.schemas
%{_sysconfdir}/xdg/autostart/bluetooth-applet.desktop
%{_bindir}/bluetooth-*
%{_libdir}/gnome-bluetooth/
%{_datadir}/applications/*.desktop
%{_datadir}/gnome-bluetooth/
%{_mandir}/man1/*
/lib/udev/rules.d/61-gnome-bluetooth-rfkill.rules

%files libs
%defattr(-,root,root,-)
%doc COPYING.LIB
%{_libdir}/libgnome-bluetooth.so.*
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/icons/hicolor/*/status/*

%files libs-devel
%defattr(-,root,root,-)
%{_includedir}/gnome-bluetooth/
%{_libdir}/libgnome-bluetooth.so
%{_libdir}/pkgconfig/gnome-bluetooth-1.0.pc
%{_datadir}/gtk-doc/html/gnome-bluetooth/

%changelog
* Tue Aug 10 2010 Bastien Nocera <bnocera@redhat.com> 2.28.6-8
- Add more killswitch patches, handle the case where the
  only killswitch disappears with the adapter
Resolves: #609291

* Tue Aug 03 2010 Bastien Nocera <bnocera@redhat.com> 2.28.6-7
- Add killswitch clean up patches
- Fix status of the applet icon when bringing back from hard
  killswitch
Resolves: #609291

* Mon May 17 2010 Matthias Clasen <mclasen@redhat.com> 2.28.6-6
- Updated translations
Resolves: #589198

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.28.6-5
- Drop unneeded scrollkeeper-update calls
Resolves: #585861

* Tue Mar 02 2010 Bastien Nocera <bnocera@redhat.com> 2.28.6-4
- Require -libs of the same version to avoid conflicts
Related: rhbz#569548

* Thu Jan 28 2010 Bastien Nocera <bnocera@redhat.com> 2.28.6-3
- Fix a few rpmlint bugs
Related: rhbz#543948

* Thu Jan 21 2010 Bastien Nocera <bnocera@redhat.com> 2.28.6-2
- Don't build on s390(x), no Bluetooth there (#557206)
Related: rhbz#543948

* Tue Dec 22 2009 Bastien Nocera <bnocera@redhat.com> 2.28.6-1
- Update to 2.28.6
Related: rhbz#543948

* Tue Dec 22 2009 Bastien Nocera <bnocera@redhat.com> 2.28.5-1
- Update to 2.28.5
Related: rhbz#543948

* Fri Dec 11 2009 Bastien Nocera <bnocera@redhat.com> 2.28.4-1
- Update to 2.28.4

* Tue Oct 20 2009 Bastien Nocera <bnocera@redhat.com> 2.28.3-1
- Update to 2.28.3

* Tue Oct 20 2009 Bastien Nocera <bnocera@redhat.com> 2.28.2-1
- Update to 2.28.2

* Tue Sep 29 2009 Bastien Nocera <bnocera@redhat.com> 2.28.1-1
- Update to 2.28.1

* Sat Sep 19 2009 Bastien Nocera <bnocera@redhat.com> 2.28.0-1
- Update to 2.28.0

* Fri Sep 11 2009 Bastien Nocera <bnocera@redhat.com> 2.27.90-3
- Fix possible pairing failure

* Thu Sep 03 2009 Bastien Nocera <bnocera@redhat.com> 2.27.90-2
- Fix connecting to audio devices not working when disconnected
  at start

* Wed Sep 02 2009 Bastien Nocera <bnocera@redhat.com> 2.27.90-1
- Update to 2.27.90

* Tue Aug 11 2009 Bastien Nocera <bnocera@redhat.com> 2.27.9-5
- Fix the friendly name not being editable (#516801)

* Tue Aug 11 2009 Bastien Nocera <bnocera@redhat.com> 2.27.9-4
- Add udev rules to access /dev/rfkill (#514798)

* Tue Aug 11 2009 Bastien Nocera <bnocera@redhat.com> 2.27.9-3
- Don't crash when exiting the wizard

* Thu Aug 06 2009 Bastien Nocera <bnocera@redhat.com> 2.27.9-2
- Remove requirement on the main package from -libs, and move
  the icons from the main package to the -libs sub-package (#515845)

* Tue Aug 04 2009 Bastien Nocera <bnocera@redhat.com> 2.27.9-1
- Update to 2.27.9

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 21 2009 Bastien Nocera <bnocera@redhat.com> 2.27.8-1
- Update to 2.27.8

* Thu Jun 25 2009 Bastien Nocera <bnocera@redhat.com> 2.27.7.1-1
- Update to 2.27.7.1

* Thu Jun 25 2009 Bastien Nocera <bnocera@redhat.com> 2.27.7-1
- Update to 2.27.7

* Wed Jun 17 2009 Bastien Nocera <bnocera@redhat.com> 2.27.6-1
- Update to 2.27.6
- Require newer BlueZ for SSP support

* Sat May 16 2009 Matthias Clasen <mclasen@redhat.com> 2.27.5-2
- Require the virtual provides for notification daemon (#500585)

* Wed May 06 2009 Bastien Nocera <bnocera@redhat.com> 2.27.5-1
- Update to 2.27.5

* Fri May 01 2009 Bastien Nocera <bnocera@redhat.com> 2.27.4-4
- Use the scriplets on the wiki for the icon update

* Fri May 01 2009 Bastien Nocera <bnocera@redhat.com> 2.27.4-3
- Touch the icon theme directory, should fix the icon not appearing
  properly on new installs

* Thu Apr 16 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.4-2
- Require the PA Bluetooth plugins

* Tue Apr 14 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.4-1
- Update to 2.27.4

* Thu Apr 09 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.3-1
- Update to 2.27.3

* Wed Apr 08 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.2-2
- Fix schema installation

* Wed Apr 08 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.2-1
- Upgrade to 2.27.2

* Tue Mar 10 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.1-4
- Make the -libs-devel obsolete and provide the -devel package, so
  we can actually upgrade...

* Thu Mar 05 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.1-3
- Add patch to fix sendto

* Wed Mar 04 2009 - Bastien Nocera <bnocera@redhat.com> - 2.27.1-2
- Update to 2.27.1
- Loads of fixes mentioned by Bill Nottingham in bug #488498

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb 19 2009 - Bastien Nocera <bnocera@redhat.com> - 0.12.0-1
- Update to 0.12.0

* Thu Dec  4 2008 Matthias Clasen <mclasen@redhat.com> - 0.11.0-8
- Rebuild for Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.11.0-7
- Rebuild for Python 2.6

* Fri Oct 31 2008 - Bastien Nocera <bnocera@redhat.com> - 0.11.0-6
- Remove a few more .la files

* Thu Sep 11 2008 Matthias Clasen  <mclasen@redhat.com> - 0.11.0-5
- Rebuild against new bluez-libs

* Wed May 14 2008 - Ondrej Vasik <ovasik@redhat.com> - 0.11.0-4
- Changed name of icon file(#444811)

* Wed Feb 27 2008 - Bastien Nocera <bnocera@redhat.com> - 0.11.0-3
- Remove gnome-obex-server, we should use gnome-user-share now

* Mon Feb 11 2008 - Ondrej Vasik <ovasik@redhat.com> - 0.11.0-1
- gcc43 rebuild

* Mon Jan 21 2008 - Bastien Nocera <bnocera@redhat.com> - 0.11.0
- Update to 0.11.0

* Mon Jan 21 2008 - Bastien Nocera <bnocera@redhat.com> - 0.10.0
- Update to 0.10.0

* Mon Oct 22 2007 - Ondrej Vasik <ovasik@redhat.com> - 0.9.1-4
- marked gnome-obex-server.schemas as config file
- changed upstream URL

* Tue Sep 18 2007 - Ondrej Vasik <ovasik@redhat.com> - 0.9.1-3
- fixed wrong source URL

* Thu Aug 23 2007 - Ondrej Vasik <ovasik@redhat.com> - 0.9.1-2
- rebuilt for F8
- changed license tag to GPLv2 and LGPLv2+

* Mon Jul 23 2007 - Bastien Nocera <bnocera@redhat.com> - 0.9.1-1
- Upgrade to 0.9.1 to fix a crasher in the server

* Thu Jul 12 2007 - Bastien Nocera <bnocera@redhat.com> - 0.9.0-1
- Update for 0.9.0
- Fix installation of the python bindings

* Mon Apr  2 2007 Matthias Clasen <mclasen@redhat.com> - 0.8.0-4
- Remove unncessary gconfd killing from scripts (#224561)

* Tue Feb 27 2007 Harald Hoyer <harald@redhat.com> - 0.8.0-3%{?dist}
- corrected BuildRoot
- smp flags added
- specfile cleanup
- fixed desktop file

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 0.8.0-2
- rebuild for python 2.5

* Mon Nov 13 2006 Harald Hoyer <harald@redhat.com> - 0.8.0-1
- version 0.8.0

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.7.0-10.1
- rebuild

* Wed Jun 14 2006 Harald Hoyer <harald@redhat.com> - 0.7.0-10
- bump for new openobex

* Sun Jun 11 2006 Jesse Keating <jkeating@redhat.com> - 0.7.0-9
- Missing automake, libtool, gettext BR

* Sun Jun 11 2006 Jesse Keating <jkeating@redhat.com> - 0.7.0-6
- Bump for new libbluetooth

* Wed May 31 2006 Harald Hoyer <harald@redhat.com> - 0.7.0-6
- add dependency on bluez-utils, cosmetic tweaks (bug #190280)

* Tue May 30 2006 Harald Hoyer <harald@redhat.com> - 0.7.0-5
- install schemata correctly (bug #193518)

* Mon May 29 2006 Harald Hoyer <harald@redhat.com> - 0.7.0-3
- more build requires (bug #193374)

* Mon Feb 27 2006 Harald Hoyer <harald@redhat.com> - 0.7.0-2
- pydir fixes for lib64

* Thu Feb 16 2006 Harald Hoyer <harald@redhat.com> - 0.7.0-1
- version 0.7.0

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.6.0-2.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.6.0-2.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Oct 07 2005 Harald Hoyer <harald@redhat.com> - 0.6.0-2
- Fix relative path for the icons in desktop files which no longer works
  with the icon cache.

* Wed Sep 28 2005 Harald Hoyer <harald@redhat.com> - 0.6.0-1
- new version 0.6.0

* Tue Aug 16 2005 Warren Togami <wtogami@redhat.com> 0.5.1-14
- rebuild for new cairo

* Thu Jul  7 2005 Matthias Saou <http://freshrpms.net/> 0.5.1-13
- Minor spec file cleanups.
- Fix relative path for the icons in desktop files which no longer works
  with the icon cache.
- Remove useless zero epochs.
- Remove explicit python abi requirement, it's automatic for FC4 and up.

* Thu Mar 31 2005 Harald Hoyer <harald@redhat.com> - 0.5.1-12
- removed base requirement from libs

* Tue Mar 29 2005 Warren Togami <wtogami@redhat.com> - 0.5.1-11
- devel req glib2-devel libbtctl-devel for pkgconfig (#152488)

* Wed Mar 02 2005 Harald Hoyer <harald@redhat.com> 
- rebuilt

* Mon Feb 21 2005 Harald Hoyer <harald@redhat.com> - 0.5.1-9
- added gnome hbox patch for bug rh#149215

* Tue Dec 07 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-8
- added requires for python-abi

* Tue Dec 07 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-7
- split package into app, libs and devel

* Mon Oct 25 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-6
- fixed again gnome-bluetooth-manager script for 64bit (bug 134864)

* Fri Oct 08 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-5
- buildrequire pygtk2-devel (bug 135032)
- fixed gnome-bluetooth-manager script for 64bit (bug 134864)
- fixed segfault on file receive (bug 133041)

* Mon Sep 27 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-4
- buildrequire libbtctl-devel
- buildrequire openobex-devel >= 1.0.1
- pythondir -> pyexecdir

* Wed Jul 28 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-3
- added build dependency for librsvg2-devel

* Tue Jul 27 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-2
- added pydir patch

* Thu Jul 22 2004 Harald Hoyer <harald@redhat.com> - 0.5.1-1
- version 0.5.1

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue May 25 2004 Harald Hoyer <harald@redhat.com> - 0.4.1-8
- corrected BuildRequires

* Wed Mar 10 2004 Harald Hoyer <harald@redhat.com> - 0.4.1-7
- added EggToolBar patch for gcc34

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jan 26 2004 Harald Hoyer <harald@redhat.de> 0.4.1-4
- added autofoo patch

* Thu Aug 28 2003 Harald Hoyer <harald@redhat.de> 0.4.1-3
- add .so to gnome-vfs module, if libtool does not!

* Thu Aug 07 2003 Harald Hoyer <harald@redhat.de> 0.4.1-2
- call libtool finish

* Wed Aug  6 2003 Harald Hoyer <harald@redhat.de> 0.4.1-1
- new version 0.4.1

* Wed Jun  5 2003 Harald Hoyer <harald@redhat.de> 0.4-1
- initial RPM


