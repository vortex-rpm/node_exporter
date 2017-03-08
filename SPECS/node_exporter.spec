%define debug_package %{nil}

%define _git_slug src/github.com/prometheus/node_exporter

Name:    node_exporter
Version: 0.13.0
Release: 1.vortex%{?dist}
Summary: Prometheus exporter for machine metrics
License: ASL 2.0
Vendor:  Vortex RPM
URL:     https://github.com/prometheus/node_exporter

Source2: %{name}.default
Source3: %{name}.init

Requires(post): chkconfig
Requires(preun): chkconfig, initscripts
Requires(pre): shadow-utils
Requires: daemonize
BuildRequires: golang, git

%description
Prometheus exporter for hardware and OS metrics exposed by *NIX kernels,
written in Go with pluggable metric collectors.

%prep
mkdir _build
export GOPATH=$(pwd)/_build
git clone https://github.com/prometheus/%{name} $GOPATH/%{_git_slug}
cd $GOPATH/%{_git_slug}
git checkout v%{version}

%build
export GOPATH=$(pwd)/_build
cd $GOPATH/%{_git_slug}
make

%install
export GOPATH=$(pwd)/_build
mkdir -vp %{buildroot}/var/lib/prometheus
mkdir -vp %{buildroot}/usr/bin
mkdir -vp %{buildroot}%{_initddir}
mkdir -vp %{buildroot}/etc/default
install -m 755 $GOPATH/%{_git_slug}/%{name} %{buildroot}/usr/sbin/%{name}
install -m 755 %{SOURCE3} %{buildroot}%{_initddir}/%{name}
install -m 644 %{SOURCE2} %{buildroot}/etc/default/%{name}

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d /var/lib/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name} restart >/dev/null 2>&1
fi

%files
%defattr(-,root,root,-)
/usr/sbin/%{name}
%{_initddir}/%{name}
%config(noreplace) /etc/default/%{name}
%attr(755, prometheus, prometheus)/var/lib/prometheus
%doc CHANGELOG.md LICENSE NOTICE README.md

%changelog
* Wed Mar 08 2017 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0.0-0.git20170119.vortex
- Initial packaging
