## Developer?

See [CONTRIBUTING.md](CONTRIBUTING.md)

## [#WeAreNotWaiting](https://twitter.com/hashtag/wearenotwaiting?src=hash&vertical=default&f=images) and [this](https://vimeo.com/109767890) is why.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Install](#install)
  - [Supported configurations:](#supported-configurations)
  - [Recommended minimum browser versions for using Nightscout:](#recommended-minimum-browser-versions-for-using-nightscout)
  - [Windows installation software requirements:](#windows-installation-software-requirements)
  - [Installation notes for users with nginx or Apache reverse proxy for SSL/TLS offloading:](#installation-notes-for-users-with-nginx-or-apache-reverse-proxy-for-ssltls-offloading)
  - [Installation notes for Microsoft Azure, Windows:](#installation-notes-for-microsoft-azure-windows)
- [Development](#development)
- [Usage](#usage)
  - [Updating my version?](#updating-my-version)
  - [Configure my uploader to match](#configure-my-uploader-to-match)


<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Install

## Supported configurations:

If you plan to use Nightscout, we recommend using [Heroku](https://nightscout.github.io/nightscout/new_user/) as this is free and easy to use.
We used to recommend hostig at Azure, but the resource needs of Nightscout have grown over the years and Azure won't comfortably run Nightscout
anymore in the free tier. If you're hosting in Azure and looking to update your site, we recommend you
[switch from Azure to Heroku](http://openaps.readthedocs.io/en/latest/docs/While%20You%20Wait%20For%20Gear/nightscout-setup.html#switching-from-azure-to-heroku)
as you're likely to hit issues in the process of updating the site.

- [Nightscout Setup with Heroku](https://nightscout.github.io/nightscout/new_user/) (recommended)

While you can install Nightscout on a virtual server or a Raspberry Pi, we do not recommend this unless you have at least some
experience hosting Node applications and development using the toolchain in use with Nightscout. Heroku automates all of the
hosting for you and even many of the dvelopers run their production sites in Heroku due to convenience.

If you're a hosting provider and want to provide our users additional free hosting options,
you're welcome to issue a documentation pull request with instructions on how to setup Nightscout on your system.

## Recommended minimum browser versions for using Nightscout:

Older versions of the browsers might work, but are untested.

Older versions of the browsers might work, but are untested.
