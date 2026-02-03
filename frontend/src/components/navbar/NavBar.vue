<script setup>

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <nav class="navbar w-full bg-base-100 shadow-sm">
        <div class="navbar-start">
          <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
            <MenuIcon/>
          </label>
          <div class="px-2 font-bold text-xl">AI Friends</div>
        </div>
        <div class="navbar-center w-4/5 max-w-180">
          <div class="join w-4/5">
            <input class="input join-item rounded-l-full w-4/5" placeholder="Search whatever you want" />
            <button class="btn join-item rounded-r-full gap-0">
              <SearchIcon/>
              Search
            </button>
          </div>
        </div>
        <div class="navbar-end">
          <button class="btn btn-ghost text-lg">login</button>
        </div>
      </nav>
      <slot></slot>
    </div>

    <div class="drawer-side is-drawer-close:overflow-visible">
      <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
      <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-54">
        <ul class="menu w-full grow">
          <li>
            <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="Menu">
              <HomepageIcon/>
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">Menu</span>
            </button>
          </li>
          <li>
            <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="Friends">
              <FriendIcon/>
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">Frineds</span>
            </button>
          </li>
          <li>
            <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="Create">
              <CreateIcon/>
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">Create</span>
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>