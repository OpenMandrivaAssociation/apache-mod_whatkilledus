Summary:	Tracks the current request and logs active requests when a child process crashes
Name:		apache-mod_whatkilledus
Version:	0
Release:	%mkrel 9
Group:		System/Servers
License:	Apache License
Group:		System/Servers
URL:		http://www.apache.org
# http://people.apache.org/~trawick/mod_whatkilledus.c
Source0: 	mod_whatkilledus.c.bz2
Source1: 	test_char.h.bz2
BuildRequires:	apache-devel
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache-base >= 2.2.0
Requires(pre):	apache-modules >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache-base >= 2.2.0
Requires:	apache-modules >= 2.2.0
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_whatkilledus is an experimental module for Apache httpd 2.x which
tracks the current request and logs a report of the active request
when a child process crashes. You should verify that it works reasonably
on your system before putting it in production.

mod_whatkilledus is called during request processing to save information
about the current request. It also implements a fatal exception hook
that will be called when a child process crashes.

%prep

%setup -c -T

bzcat %{SOURCE0} > mod_whatkilledus.c
bzcat %{SOURCE1} > test_char.h

%build

%{_sbindir}/apxs `apr-config --includes` -c mod_whatkilledus.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}/var/log/httpd

cat << EOF > %{buildroot}/%{_sysconfdir}/httpd/modules.d/ZZ91_mod_whatkilledus.conf
<IfDefine HAVE_WHATKILLEDUS>
  <IfModule !mod_whatkilledus.so.c>
    LoadModule whatkilledus_module		extramodules/mod_whatkilledus.so
  </IfModule>
</IfDefine>

<IfModule mod_whatkilledus.c>
    EnableExceptionHook On
    WhatKilledUsLog logs/whatkilledus_log
</IfModule>
EOF

install -m0755 .libs/mod_whatkilledus.so %{buildroot}%{_libdir}/apache-extramodules/

touch %{buildroot}/var/log/httpd/whatkilledus_log

%post
%create_ghostfile /var/log/httpd/whatkilledus_log apache apache 0644
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 

%files
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/ZZ91_mod_whatkilledus.conf
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_whatkilledus.so
%attr(0644,apache,apache) %ghost /var/log/httpd/whatkilledus_log


