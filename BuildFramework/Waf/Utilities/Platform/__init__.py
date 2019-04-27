from __future__ import absolute_import, division, print_function

import platform
import re

## \package Waf.Utilities.Platform
## Contains code related to the running platform (e.g. Windows or Linux, x86 or x64, CentOS 5 or 7).

## Returns whether the system is Windows.
## \return  True if Windows.  False otherwise.
def IsWindows():
    is_windows = ('Windows' == platform.system())
    return is_windows

## Returns whether the system is Linux.
## \return  True if Linux.  False otherwise.
def IsLinux():
    is_linux = ('Linux' == platform.system())
    return is_linux

## Returns the RHEL (CentOS) RPM-style dist tag, e.g. ".el5" or ".el7".  See https://fedoraproject.org/wiki/Packaging:DistTag.
## This returns 'debian' if the platform is not RHEL (CentOS).  Note that on a CentOS 7 system, the RPM-default dist macro
## is defined as ".el7.centos" in /etc/rpm/macros.dist, but we only use the ".el7" part.
## \return  The RPM-style dist tag, e.g. ".el5" or ".el7", if the platform is RHEL (CentOS).  Otherwise, 'debian'.
def GetDistTag():
    # GET THE RHEL (CENTOS) VERSION NUMBER.
    rhel_version_match = re.search("\.el\d", platform.release())
    if not rhel_version_match:
        # The other major family of Linux distributions is based on Debian.
        #  For now, assume that anything that isn't some redhat-based Linux
        # is Debian-based.
        return ".debian"
    
    # THE DIST TAG IS THE WHOLE MATCH (GROUP 0).
    dist_tag = rhel_version_match.group(0)
    return dist_tag

## Returns the RHEL (CentOS) major version number, e.g. 5 or 7.  If the platform is not RHEL (CentOS), None is returned.
## \return  The RHEL (CentOS) major version number, e.g. 5 or 7.  If the platform is not RHEL (CentOS), None is returned.
def GetCentOSMajorVersionNumber():
    # GET THE RHEL (CENTOS) VERSION NUMBER.
    rhel_version_match = re.search("\.el(\d)", platform.release())
    if not rhel_version_match:
        return None

    # CONVERT THE VERSION NUMBER STRING TO AN INTEGER, AND RETURN IT.
    major_version_number = int(rhel_version_match.group(1))
    return major_version_number

## Returns whether the platform is RHEL 7 (CentOS 7).
## \return  True if the platform is RHEL 7 (CentOS 7).  False otherwise.
def IsCentOS7():
    # RETURN WHETHER THE MAJOR VERSION NUMBER IS 7.
    is_centos_7 = (7 == GetCentOSMajorVersionNumber())
    return is_centos_7

## Returns whether the platform is RHEL 5 (CentOS 5).
## \return  True if the platform is RHEL 5 (CentOS 5).  False otherwise.
def IsCentOS5():
    # RETURN WHETHER THE MAJOR VERSION NUMBER IS 5.
    is_centos_5 = (5 == GetCentOSMajorVersionNumber())
    return is_centos_5

## Returns whether the platform is RHEL 6 (CentOS 6).
## \return  True if the platform is RHEL 6 (CentOS 6).  False otherwise.
def IsCentOS6():
    # RETURN WHETHER THE MAJOR VERSION NUMBER IS 6.
    is_centos_6 = (6 == GetCentOSMajorVersionNumber())
    return is_centos_6

## Returns the major version number from a decimal string, e.g. 12.04
## or 16.10.  If the provided decimal string isn't formatted as expected,
## None is returned.
## \param[in]   version_number_string - The string containing the full version number.
def GetMajorVersionNumberFromDecimalString(version_number_string):
    # GET THE MAJOR VERSION NUMBER FROM THE FULL VERSION NUMBER.
    major_version_match = re.search("(\d+)\.", version_number_string)
    if not major_version_match:
        return None

    # CONVERT THE VERSION NUMBER STRING TO AN INTEGER, AND RETURN IT.
    major_version_number = int(major_version_match.group(1))
    return major_version_number

## Returns whether the platform is Ubuntu 12.
## \return  True if the platform is Ubuntu 12.  False otherwise.
def IsUbuntu12():
    # GET THE LINUX DISTRIBUTION INFORMATION.
    (linux_distribution,version_number,version_codename) = platform.linux_distribution()
    
    # VERIFY THE DISTRIBUTION IS UBUNTU.
    UBUNTU_DISTRIBUTION_NAME = 'ubuntu'
    is_ubuntu = (UBUNTU_DISTRIBUTION_NAME == linux_distribution.lower())
    if not is_ubuntu:
        return False
    
    # RETURN WHETHER THE MAJOR VERSION NUMBER IS 12.
    is_ubuntu_12 = (12 == GetMajorVersionNumberFromDecimalString(version_number))
    return is_ubuntu_12
    

